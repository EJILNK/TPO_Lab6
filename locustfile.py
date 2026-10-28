from locust import HttpUser, task, between
import urllib3


# OpenBMC использует самоподписанный HTTPS-сертификат.
# Убираем предупреждения о том, что сертификат не проверяется.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# ============================================================
# Нагрузочное тестирование OpenBMC
# ============================================================

class OpenBMCUser(HttpUser):
    # Адрес нашего OpenBMC.
    # Порт 8443 на Ubuntu проброшен в QEMU на порт 443 OpenBMC.
    host = "https://127.0.0.1:8443"

    # Виртуальный пользователь будет ждать от 1 до 3 секунд
    # между выполнением запросов.
    wait_time = between(1, 3)

    @task
    def get_system_info(self):
        """
        Получение общей информации о системе OpenBMC.
        """

        self.client.get(
            "/redfish/v1/Systems/system",
            auth=("root", "0penBmc"),
            verify=False,
            name="OpenBMC: system info"
        )

    @task
    def get_power_state(self):
        """
        Получение состояния питания системы.
        PowerState находится внутри ответа
        /redfish/v1/Systems/system.
        """

        with self.client.get(
            "/redfish/v1/Systems/system",
            auth=("root", "0penBmc"),
            verify=False,
            name="OpenBMC: PowerState",
            catch_response=True
        ) as response:

            # Проверяем, что сервер вообще нормально ответил.
            if response.status_code != 200:
                response.failure(
                    f"Ошибка HTTP: {response.status_code}"
                )
                return

            # Получаем JSON из ответа OpenBMC.
            try:
                data = response.json()
            except ValueError:
                response.failure("OpenBMC вернул не JSON")
                return

            # Проверяем наличие поля PowerState.
            if "PowerState" not in data:
                response.failure("Поле PowerState отсутствует")


# ============================================================
# Нагрузочное тестирование публичных API
# ============================================================

class PublicAPIUser(HttpUser):
    # Основной публичный API.
    host = "https://jsonplaceholder.typicode.com"

    wait_time = between(1, 3)

    @task
    def get_posts(self):
        """
        Получение списка постов JSONPlaceholder.
        """

        self.client.get(
            "/posts",
            name="JSONPlaceholder: /posts"
        )

    @task
    def get_weather(self):
        """
        Получение информации о погоде
        для Новосибирска через wttr.in.
        """

        self.client.get(
            "https://wttr.in/Novosibirsk?format=j1",
            name="wttr.in: Novosibirsk weather"
        )
