import irsdk
import yaml


class Session(object):
    def __init__(self, ir):
        if not isinstance(ir, irsdk.IRSDK):
            raise TypeError("ir must be an IRSDK instance")

        self.ir = ir
        self._session_info = None

        if not self.ir.is_connected:
            raise ConnectionError("Not connected to IRacing")

    def refresh(self):
        self._update_session_info()

    def _update_session_info(self):
        session_info_yaml = self.ir["SessionInfo"]
        if session_info_yaml:
            try:
                parsed_yaml = yaml.safe_load(session_info_yaml)
                print(parsed_yaml)
                if parsed_yaml != self.session_info:
                    self.session_info = parsed_yaml
            except yaml.YAMLError as e:
                print(f"Error parsing session info yaml: {e} ")
                self.session_info = None
        else:
            self.session_info = None


    @property
    def track_name(self):
        if self._session_info:
            return self._session_info["TrackName"]
