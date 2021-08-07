from config import settings
from fullfii.lib.utils import check_is_maintaining


def gene_maintenance_message():
    return "実施中" if check_is_maintaining(settings.BASE_DIR) else ""
