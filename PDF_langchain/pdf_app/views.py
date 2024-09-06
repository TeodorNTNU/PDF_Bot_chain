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
from .uploader import upload_pdf_to_vector_db
from django.db import transaction
from concurrent.futures import ThreadPoolExecutor

class PDFViewSet(viewsets.ModelViewSet):
    queryset = PDF.objects.all()
    serializer_class = PDFSerializer

    def create(self, request, *args, **kwargs):
        if 'pdf_files' not in request.FILES:
            return Response({'error': 'No files provided'}, status=status.HTTP_400_BAD_REQUEST)

        pdf_instances = []
        uploaded_files = []

        with transaction.atomic():
            PDFs_to_insert = []
            for pdf_file in request.FILES.getlist('pdf_files'):
                name = pdf_file.name.rsplit('.', 1)[0]

                if PDF.objects.filter(name=name).exists():
                    continue

                pdf_instance = PDF(name=name, pdf_file=pdf_file)
                PDFs_to_insert.append(pdf_instance)

            PDF.objects.bulk_create(PDFs_to_insert)

            for pdf_instance in PDFs_to_insert:
                pdf_instance.save()
                uploaded_files.append(pdf_instance.pdf_file.path)

        # Upload files to vector database asynchronously
        with ThreadPoolExecutor() as executor:
            future_to_file = {executor.submit(upload_pdf_to_vector_db, file_path): file_path for file_path in uploaded_files}
            for future in future_to_file:
                try:
                    future.result()
                except Exception as e:
                    error_message = f"Error uploading to vector database: {str(e)}"
                    print(error_message)
                    return Response({'error': error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'success': 'All PDFs uploaded successfully!'}, status=status.HTTP_201_CREATED)

from channels.generic.websocket import AsyncWebsocketConsumer
import json
from .retriever import conversational_rag_chain, rag_chain
import sys
from .models import ChatMessage  # Import the ChatMessage model

class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        print("WebSocket connection attempt")  # Log connection attempt
        await self.accept()
        print("WebSocket connection accepted")  # Log successful connection

    async def disconnect(self, close_code):
        print(f"WebSocket disconnected with close code {close_code}")  # Log disconnect

    async def receive(self, text_data):
        print(f"Received message: {text_data}")  # Log incoming message
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        #session_id = text_data_json.get("session_id", "default_session")  # Retrieve session_id or use a default

        # Save the incoming message to the database
        #await self.save_message(session_id, "user", message)
        try:
            # Stream the response from the RAG chain
            payload = {'input': message}
            print(f"Input payload: {payload}")  # Debugging input format
            async for chunk in conversational_rag_chain.astream_events(payload, 
            config={'configurable': {'session_id': 'abc123'}}, version="v2"):
                event = chunk['event']
                if event in ["on_parser_start", "on_parser_stream"]:
                    #print(f"Sending chunk: {chunk}")  # Log outgoing chunk
                    await self.send(text_data=json.dumps(chunk))
                if event == "on_chat_model_stream":
                # Safely accessing nested keys
                    data = chunk.get("data", {})
                    if 'chunk' in data:
                        content = data['chunk'].content
                        
                        #if content:
                        print(content, end='')
                        sys.stdout.flush()  # Ensures immediate output to console
                        #await self.save_message(session_id, "bot", content)
        except Exception as e:
            error_message = f"Error in WebSocket communication: {e}"
            print(error_message)  # Log error
            await self.send(text_data=json.dumps({"error": error_message}))
            await self.close()  # Close the WebSocket connection on error

#     @staticmethod
#     async def save_message(session_id, sender, message):
#         print(f"Saving message: session_id={session_id}, sender={sender}, message={message}")
#         ChatMessage.objects.create(session_id=session_id, sender=sender, message=message)
