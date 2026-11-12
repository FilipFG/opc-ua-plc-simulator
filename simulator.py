import asyncio
import logging
import random
from asyncua import Client, ua

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)


async def main():
    url = "opc.tcp://192.168.0.5:4840"

    async with Client(url=url) as client:
        _logger.info("Połączono z PLC S7-1500!")

        # Ścieżki do obu zmiennych w bloku Test_OPCUA[cite: 2]
        node_write_path = 'ns=3;s="Test_OPCUA"."Test_write"'
        node_read_path = 'ns=3;s="Test_OPCUA"."Test_read"'

        node_write = client.get_node(node_write_path)
        node_read = client.get_node(node_read_path)

        _logger.info(
            "Uruchomiono pętlę komunikacji. Naciśnij Ctrl+C, aby zatrzymać."
        )

        try:
            while True:
                # 1. Losowanie liczby od 0 do 10 przez klienta (Python)
                random_val = random.randint(0, 10)

                # 2. Zapis do PLC (wymuszenie typu ua.VariantType.Int16,
                # żeby S7-1500 poprawnie przyjął zmienną typu Int)
                await node_write.set_value(
                    ua.DataValue(
                        ua.Variant(random_val, ua.VariantType.Int16)
                    )
                )

                # 3. Odczyt wartości z obu zmiennych ze sterownika
                val_w = await node_write.get_value()
                val_r = await node_read.get_value()

                print(
                    f"[OPC-UA] Wysłano do Test_write: {random_val} | Odczytano z PLC -> Test_write: {val_w}, Test_read: {val_r}"
                )

                # Odstęp 1 sekunda
                await asyncio.sleep(1.0)

        except asyncio.CancelledError:
            _logger.info("Zatrzymano pętlę.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProgram zakończony przez użytkownika.")