"""Inicializa la estructura de directorios del proyecto."""
import os
from pathlib import Path


def init_directories(base_path: Path = None):
    """Crea los directorios necesarios para la ejecución."""
    if base_path is None:
        base_path = Path(__file__).parent.parent / "data"
    
    directories = [
        base_path / "urls_iniciales",
        base_path / "resultados",
        base_path / "logs",
        base_path / "backup",
    ]
    
    for dir_path in directories:
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"[OK] {dir_path}")
    
    # Crear CSV template si no existe
    template_path = base_path / "urls_iniciales" / "template.csv"
    if not template_path.exists():
        template_path.write_text(
            "url,nicho,prioridad\n"
            "https://ejemplo.cl,construccion,1\n"
        )
        print(f"[OK] Template creado: {template_path}")


if __name__ == "__main__":
    init_directories()
