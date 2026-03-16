from fastapi import Depends

from app.application.use_cases import GatewayService
from app.core.config import Settings, get_settings
from app.infrastructure.clients import ServiceClients


def get_service_clients(settings: Settings = Depends(get_settings)) -> ServiceClients:
    return ServiceClients(settings)


def get_gateway_service(
    clients: ServiceClients = Depends(get_service_clients),
    settings: Settings = Depends(get_settings),
) -> GatewayService:
    return GatewayService(clients, settings)
