# Contrato por implementar

Usar los campos y tipos de ../ACUERDOS_TECNICOS.md en messaging.proto.
Servicio previsto: MessagingService; método EnviarMensaje; mensajes Mensaje y Acuse.
Mensaje y Acuse usan message_id, sender, timestamp y message.
message es string UTF-8; payload_bytes mide su contenido codificado, sin metadatos.
El acuse conserva message_id y lleva el reloj del nodo que responde.
Documentar generación con grpcio-tools e incluir el contrato en el informe.
