from dataclasses import dataclass
from time import perf_counter_ns

from requests import RequestException, get


@dataclass(frozen=True)
class RequestResult:
    duration_ms: float
    size_bytes: int


@dataclass(frozen=True)
class BatchResult:
    average_duration_ms: float
    total_size_bytes: int
    download_speed_bytes_per_second: float


def measure_request(
    url: str,
    timeout: int = 120,
    chunk_size: int = 64 * 1024,
) -> RequestResult:
    start_ns = perf_counter_ns()

    with get(url, stream=True, timeout=timeout) as response:
        response.raise_for_status()
        size_bytes = sum(
            len(chunk) for chunk in response.iter_content(chunk_size=chunk_size)
        )

    duration_ms = (perf_counter_ns() - start_ns) / 1_000_000

    return RequestResult(
        duration_ms=duration_ms,
        size_bytes=size_bytes,
    )


def measure_batch(
    url: str,
    count: int = 10,
    timeout: int = 120,
    chunk_size: int = 64 * 1024,
) -> BatchResult:
    if count <= 0:
        raise ValueError("Количество запросов должно быть больше нуля")

    results = [
        measure_request(url, timeout=timeout, chunk_size=chunk_size)
        for _ in range(count)
    ]

    total_duration_ms = sum(result.duration_ms for result in results)
    total_size_bytes = sum(result.size_bytes for result in results)

    return BatchResult(
        average_duration_ms=total_duration_ms / count,
        total_size_bytes=total_size_bytes,
        download_speed_bytes_per_second=total_size_bytes / (total_duration_ms / 1000),
    )


def main() -> None:
    url = input("Введите URL: ").strip()

    try:
        result = measure_batch(url)
    except RequestException as error:
        print(f"Ошибка запроса: {error}")
        return

    print(f"Скорость скачивания: {result.download_speed_bytes_per_second:.2f} байт/с")


if __name__ == "__main__":
    main()