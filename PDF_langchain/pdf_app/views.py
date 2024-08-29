from rest_framework import viewsets, status
from rest_framework.response import Response
import os
from .models import Item
from .serializers import ItemSerializer


class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer


from .models import PDF
from .serializers import PDFSerializer
from .uploader import upload_pdf_to_vector_db  # Import the function from uploader.py
from django.db import transaction  # Import transaction to manage DB operations

class PDFViewSet(viewsets.ModelViewSet):
    queryset = PDF.objects.all()
    serializer_class = PDFSerializer

    def create(self, request, *args, **kwargs):
        if 'pdf_files' not in request.FILES:
            return Response({'error': 'No files provided'}, status=status.HTTP_400_BAD_REQUEST)

        pdf_instances = []
        uploaded_files = []

        # Create a list of unsaved PDF model instances
        PDFs_to_insert = []

        for pdf_file in request.FILES.getlist('pdf_files'):
            name = pdf_file.name.rsplit('.', 1)[0]  # Extract file name without extension

            # Check for duplicates
            if PDF.objects.filter(name=name).exists():
                continue  # Skip duplicate files

            # Create PDF instance and add to the list
            pdf_instance = PDF(name=name, pdf_file=pdf_file)
            PDFs_to_insert.append(pdf_instance)

        # Use bulk_create to save all PDF instances in a single query
        PDF.objects.bulk_create(PDFs_to_insert)

        # Manually save each file to ensure it is uploaded to the media directory
        for pdf_instance in PDFs_to_insert:
            pdf_instance.save()  # This will save the file to the media directory
            uploaded_files.append(pdf_instance.pdf_file.path)  # Keep track of file paths

        # After saving to the database, upload the files to the vector database
        for file_path in uploaded_files:
            try:
                upload_pdf_to_vector_db(file_path)
            except Exception as e:
                error_message = f"Error uploading to vector database: {str(e)}"
                print(error_message)
                return Response({'error': error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'success': 'All PDFs uploaded successfully!'}, status=status.HTTP_201_CREATED)

from channels.generic.websocket import AsyncWebsocketConsumer
import json
from .retriever import rag_chain

class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        try:
            # Stream the response from the RAG chain
            async for chunk in rag_chain.astream_events({'input': message}, version="v1"):
                if chunk["event"] in ["on_parser_start", "on_parser_stream"]:
                    await self.send(text_data=json.dumps(chunk))

        except Exception as e:
            print(f"Error in WebSocket communication: {e}")
            await self.send(text_data=json.dumps({"error": str(e)}))
            await self.close()  # Optionally close the WebSocket connection on error
