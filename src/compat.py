"""
Parches de compatibilidad con el entorno de Google Colab.

Colab trae preinstalado un torchao viejo (0.10) y las versiones recientes de peft
lanzan ImportError al crear/cargar un LoRA si lo encuentran, aunque no lo usemos
(no hay cuantización). Sin este parche solucion.py fallaría en el Colab del docente.
"""
import sys


def parchear_torchao() -> None:
    """Si torchao es incompatible con peft, peft lo trata como no instalado."""
    import peft
    import peft.import_utils as iu

    if not hasattr(iu, "is_torchao_available"):
        return
    try:
        iu.is_torchao_available()
        return  # torchao ausente o compatible: no hay nada que parchear
    except ImportError:
        pass

    def _no_disponible() -> bool:
        return False

    # Reemplazar también las copias importadas con "from peft.import_utils import ..."
    for nombre, modulo in list(sys.modules.items()):
        if nombre.startswith("peft") and hasattr(modulo, "is_torchao_available"):
            modulo.is_torchao_available = _no_disponible
