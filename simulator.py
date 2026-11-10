import argparse
import asyncio
import logging
import sys
from asyncua import Client, Server, ua

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("OPC-UA-Simulator")


async def run_server(port: int):
    """Uruchamia symulator stacji zgrzewania jako Serwer OPC UA."""
    server = Server()
    await server.init()

    endpoint = f"opc.tcp://0.0.0.0:{port}/freeopcua/server/"
    server.set_endpoint(endpoint)
    server.set_server_name("Simatic S7-1500 Welding Station Simulator")

    # Ustawienie polityki bezpieczeństwa (opcjonalnie można dostosować)
    server.set_security_policy(
        [
            ua.SecurityPolicyType.NoSecurity,
            ua.SecurityPolicyType.Basic256Sha256_SignAndEncrypt,
        ]
    )

    # Rejestracja przestrzeni nazw
    uri = "http://examples.freeopcua.github.io"
    idx = await server.register_namespace(uri)

    # Tworzenie struktury węzłów dla Stacji Zgrzewania
    station_node = await server.nodes.objects.add_folder(idx, "StacjaZgrzewania")

    # Zmienne procesowe
    var_temp = await station_node.add_variable(idx, "TempElektrody", 22.0)
    var_counter = await station_node.add_variable(idx, "LicznikZgrzewow", 0)
    var_status = await station_node.add_variable(
        idx, "StanStacji", 0
    )  # 0: Gotowa, 1: Zgrzewanie, 99: Awaria
    var_start = await station_node.add_variable(idx, "StartCyklu", False)

    # Umożliwienie zapisu zmiennych przez klientów (np. PLC)
    await var_temp.set_writable()
    await var_counter.set_writable()
    await var_status.set_writable()
    await var_start.set_writable()

    logger.info(f"Serwer OPC UA uruchomiony na adresie: {endpoint}")
    logger.info("Rozpoczynam symulację procesu zgrzewania...")

    async with server:
        current_temp = 22.0
        cycles = 0
        while True:
            # Sprawdzenie czy cykl został wyzwolony
            start_triggered = await var_start.get_value()

            if start_triggered:
                await var_status.set_value(1)  # Stan: Zgrzewanie
                current_temp += 3.5  # Szybki wzrost temperatury podczas zgrzewania
                logger.info(
                    f"Cykl zgrzewania aktywny! Temperatura elektrody: {current_temp:.1f} °C"
                )

                if current_temp > 85.0:
                    logger.warning(
                        "!!! ALARM: Przegrzanie elektrody zgrzewalniczej (>85°C) !!!"
                    )
                    await var_status.set_value(99)  # Stan: Awaria/Przegrzanie

                # Symulacja zakończenia cyklu po chwili
                cycles += 1
                await var_counter.set_value(cycles)
                await asyncio.sleep(2)
                await var_start.set_value(False)  # Reset flagi startu
            else:
                # Chłodzenie w stanie spoczynku
                if current_temp > 22.0:
                    current_temp = max(22.0, current_temp - 1.0)

                await var_status.set_value(0)  # Stan: Gotowa

            await var_temp.set_value(round(current_temp, 1))
            await asyncio.sleep(1)


async def run_client(url: str):
    """Uruchamia symulator jako Klient OPC UA łączący się z PLC."""
    client = Client(url=url)
    logger.info(f"Łączenie z serwerem PLC pod adresem: {url}...")

    async with client:
        logger.info("Połączono pomyślnie z PLC!")

        # Przykładowe odpytywanie zmiennej (Polling) w pętli
        try:
            while True:
                # Uwaga: Ścieżka węzła NodeId zależy od konfiguracji w TIA Portal
                # Przykład standardowego bloku DB w S7-1500:
                temp_node = client.get_node('ns=3;s="DB_Zgrzewarka"."TempElektrody"')
                val = await temp_node.get_value()

                logger.info(f"[POLL] Odczytana temperatura z PLC: {val} °C")
                await asyncio.sleep(2)
        except KeyboardInterrupt:
            logger.info("Zatrzymywanie klienta przez użytkownika...")


def main():
    parser = argparse.ArgumentParser(
        description="Symulator OPC UA dla Stacji Zgrzewania i PLC S7-1500"
    )
    parser.add_argument(
        "--mode",
        choices=["server", "client"],
        required=True,
        help="Tryb działania: 'server' (Python jako serwer) lub 'client' (Python jako klient)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=4840,
        help="Port dla serwera OPC UA (domyślnie: 4840)",
    )
    parser.add_argument(
        "--url",
        type=str,
        default="opc.tcp://192.168.0.1:4840",
        help="Adres URL serwera OPC UA (używane w trybie klienta)",
    )

    args = parser.parse_args()

    try:
        if args.mode == "server":
            asyncio.run(run_server(args.port))
        elif args.mode == "client":
            asyncio.run(run_client(args.url))
    except KeyboardInterrupt:
        logger.info("Program został przerwany.")
        sys.exit(0)


if __name__ == "__main__":
    main()