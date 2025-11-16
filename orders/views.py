from django.db import transaction
from django.contrib.auth.models import User
from telegram.service import TelegramService
from typing import cast
from contextlib import AbstractContextManager
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from orders.serializers import OrderSerializer
from orders.models import Ticket, TicketStatus, Order
from orders.types import SerializedOrderDataType
from printer.service import PrintService


class OrderView(APIView):

    def post(self, request: Request):
        user = request.user
        
        f"""
            Recebe:
            
            Usuário da autenticação;
            
            {
                "ticket": int,
                "dishes": [
                    {
                        "dish_uuid": UUID,
                        "amount": float,
                        "dish_note": str | None
                        "side_dishes": [
                            {
                                "side_dish_uuid": UUID,
                            }
                        ]
                    }
                ],
                "general_note": str | None,
            }
        """
        
        serializer = OrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        # Verifica se existe ticket aberto, se existir adiciona o pedido ao ticket, senão cria um novo ticket
        with cast(AbstractContextManager, transaction.atomic()):
            ticket = Ticket.objects.filter(status=TicketStatus.OPEN).first()
            if not ticket:
                ticket = Ticket.objects.create(created_by=user, status=TicketStatus.OPEN)
                
            # Adiciona o pedido ao ticket
            ticket.orders.add(serializer.instance)
            ticket.save()
            
            serialized_order_data: SerializedOrderDataType = cast(SerializedOrderDataType, serializer.instance)        
        
            # Cria pedido
            order = Order.objects.create(
                ticket = serialized_order_data["ticket"],
                waiter = user,
                note = serialized_order_data["general_note"],
                dishes = serialized_order_data["dishes"]
            )
            
             # Envia pedido para impressão
            print_service = PrintService()
            printed, _, response_text = print_service.print_order(order)
            if not printed:
                raise Exception(f"Erro ao imprimir pedido: {response_text}")
            
        # Envia notificação para o telegram
        telegram_service = TelegramService()
        telegram_service.send_order_notification(order)
            
        return Response(status=status.HTTP_200_OK)