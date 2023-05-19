# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from ovos_config.locale import setup_locale
from ovos_utils import wait_for_exit_signal
from ovos_utils.log import init_service_logger
from ovos_utils.process_utils import reset_sigint_handler

from ovos_listener.service import SpeechService, on_error, on_stopping, on_ready


def main(ready_hook=on_ready, error_hook=on_error, stopping_hook=on_stopping,
         watchdog=lambda: None):
    reset_sigint_handler() # why is this needed again? TODO remove usage across all repos after investigating
    init_service_logger("voice")
    setup_locale()
    service = SpeechService(on_ready=ready_hook,
                            on_error=error_hook,
                            on_stopping=stopping_hook,
                            watchdog=watchdog)
    service.daemon = True
    service.start()
    wait_for_exit_signal()


if __name__ == "__main__":
    main()
