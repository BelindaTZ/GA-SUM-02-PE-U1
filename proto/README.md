# Contrato pendiente

Crear messaging.proto: servicio MessagingService, método EnviarMensaje, Mensaje y Acuse.
Mensaje incluye sender, timestamp y message, más identificador para correlacionar eventos.
Decidir si message es string o bytes y medir tamaños de carga de igual forma en TCP.
Acuse debe permitir actualizar Lamport si representa un mensaje del nodo receptor.
Documentar generación con grpcio-tools e incluir el contrato en el informe.
