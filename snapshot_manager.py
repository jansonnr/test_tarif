import json
import os
from typing import Dict, Any


class SnapshotManager:
    def __init__(self, env, snapshots_dir):
        self.env = env
        self.snapshots_dir = snapshots_dir
        os.makedirs(snapshots_dir, exist_ok=True)

    def get_snapshot_path(self, snapshot_name: str) -> str:
        return os.path.join(self.snapshots_dir, f"{snapshot_name}.json")

    def save_snapshot(self, snapshot_name: str, data: Dict[Any, Any]):
        """Сохраняет снепшот ответа"""
        path = self.get_snapshot_path(snapshot_name)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


    def load_snapshot(self, snapshot_name: str) -> Dict[Any, Any]:
        """Загружает снепшот"""
        path = self.get_snapshot_path(snapshot_name)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Снепшот не найден: {path}. Запустите с --update-snapshots")

    def snapshot_exists(self, snapshot_name: str) -> bool:
        """Проверяет существование снепшота"""
        return os.path.exists(self.get_snapshot_path(snapshot_name))