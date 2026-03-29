from fastapi import Depends

from app.application.use_cases import GatewayService
from app.core.config import Settings, get_settings
from app.infrastructure.clients import ServiceClients
from app.infrastructure.job_store import JobStore
from app.infrastructure.storage import LocalAssetStore


def get_asset_store(settings: Settings = Depends(get_settings)) -> LocalAssetStore:
    return LocalAssetStore(settings.asset_dir)


def get_job_store(asset_store: LocalAssetStore = Depends(get_asset_store)) -> JobStore:
    return JobStore(asset_store.jobs_dir)


def get_service_clients(settings: Settings = Depends(get_settings)) -> ServiceClients:
    return ServiceClients(settings)


def get_gateway_service(
    clients: ServiceClients = Depends(get_service_clients),
    settings: Settings = Depends(get_settings),
    asset_store: LocalAssetStore = Depends(get_asset_store),
    job_store: JobStore = Depends(get_job_store),
) -> GatewayService:
    return GatewayService(clients, settings, asset_store, job_store)
