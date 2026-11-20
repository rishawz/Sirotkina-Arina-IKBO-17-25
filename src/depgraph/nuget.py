"""Получение прямых зависимостей пакета NuGet по URL репозитория.

Используется протокол NuGet v3 (Package Content, "flat container"):
файл описания пакета лежит по адресу
``{repo}/{id}/{version}/{id}.nuspec``, где id и version - в нижнем
регистре. Менеджеры пакетов и сторонние библиотеки не применяются.
"""

import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass

from depgraph.errors import SourceError

HTTP_TIMEOUT = 15
HTTP_NOT_FOUND = 404
DEPENDENCY_TAG = "dependency"


@dataclass(frozen=True)
class Dependency:
    """Прямая зависимость: имя пакета и диапазон версий из nuspec."""

    name: str
    version_range: str


def build_url(repo, *parts):
    """Склеивает адрес ресурса; все части приводятся к нижнему регистру."""
    return "/".join([repo.rstrip("/"), *[part.lower() for part in parts]])


def nuspec_url(repo, package, version):
    """Возвращает адрес nuspec-файла заданной версии пакета."""
    return build_url(repo, package, version, f"{package}.nuspec")


def fetch_text(url):
    """Загружает текстовый ресурс по HTTP(S)."""
    try:
        with urllib.request.urlopen(url, timeout=HTTP_TIMEOUT) as response:
            return response.read().decode("utf-8-sig")
    except urllib.error.HTTPError as error:
        if error.code == HTTP_NOT_FOUND:
            raise SourceError(f"пакет или версия не найдены: {url}") from error
        raise SourceError(f"HTTP {error.code} при запросе {url}") from error
    except (urllib.error.URLError, TimeoutError, ValueError) as error:
        raise SourceError(f"не удалось загрузить {url}: {error}") from error


def local_name(tag):
    """Убирает пространство имён XML из имени тега."""
    return tag.rsplit("}", 1)[-1]


def parse_nuspec(text):
    """Извлекает прямые зависимости из текста nuspec.

    Зависимости всех групп targetFramework объединяются; при повторе
    имени сохраняется первое вхождение.
    """
    try:
        root = ET.fromstring(text.encode("utf-8"))
    except ET.ParseError as error:
        raise SourceError(f"некорректный nuspec: {error}") from error
    found = {}
    for element in root.iter():
        name = element.get("id")
        if local_name(element.tag) == DEPENDENCY_TAG and name:
            version_range = element.get("version", "")
            found.setdefault(name.casefold(), Dependency(name, version_range))
    return list(found.values())


def get_dependencies(repo, package, version, fetch=fetch_text):
    """Возвращает прямые зависимости пакета указанной версии."""
    return parse_nuspec(fetch(nuspec_url(repo, package, version)))
