"""Выбор конкретной версии пакета по диапазону из nuspec."""

import json

from depgraph.errors import SourceError
from depgraph.nuget import build_url, fetch_text

RANGE_OPENERS = "[("
WILDCARD = "*"
PRERELEASE_MARK = "-"


def lower_bound(version_range):
    """Возвращает нижнюю границу диапазона версий NuGet.

    NuGet выбирает минимальную подходящую версию, поэтому именно она
    используется для перехода к зависимостям. Если нижней границы нет
    (пустой диапазон, "(,1.0]", "1.*"), возвращается None.
    """
    text = version_range.strip()
    if not text:
        return None
    if text[0] in RANGE_OPENERS:
        text = text[1:-1].split(",")[0].strip()
    if not text or WILDCARD in text:
        return None
    return text


def latest_version(repo, package, fetch=fetch_text):
    """Возвращает последнюю (предпочтительно стабильную) версию пакета."""
    url = build_url(repo, package, "index.json")
    try:
        versions = json.loads(fetch(url))["versions"]
    except (ValueError, KeyError, TypeError) as error:
        raise SourceError(f"некорректный список версий: {url}") from error
    stable = [item for item in versions if PRERELEASE_MARK not in item]
    candidates = stable or versions
    if not candidates:
        raise SourceError(f"у пакета {package} нет версий")
    return candidates[-1]
