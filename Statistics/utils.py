from django.utils import timezone

from datetime import datetime

def get_current_month_range(use_jalali: bool = False):
    now = timezone.now()

    if use_jalali:
        try:
            import jdatetime
            j_now = jdatetime.datetime.now()
            j_start = jdatetime.datetime(j_now.year, j_now.month, 1, 0, 0, 0)
            g_start = j_start.togregorian()
            start_date = timezone.make_aware(
                datetime(g_start.year, g_start.month, g_start.day, 0, 0, 0)
            )
            return start_date, now
        except ImportError:
            pass

    start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    return start_date, now
