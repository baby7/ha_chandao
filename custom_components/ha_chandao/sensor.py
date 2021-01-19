"""
Support for ha chandao
# Author:
    baby7
# Created:
    2021-01-19
"""
import logging
from homeassistant.const import (
    CONF_API_KEY, CONF_NAME, ATTR_ATTRIBUTION, CONF_ID
)
from homeassistant.helpers.entity import Entity
import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA
import requests
import warnings
import json
import re

_Log = logging.getLogger(__name__)

DEFAULT_NAME = 'ha_chandao'
URL = 'url'
USERNAME = 'username'
PASSWORD = 'password'
PROJECT_ID = 'project_id'
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(URL): cv.string,
    vol.Required(USERNAME): cv.string,
    vol.Required(PASSWORD): cv.string,
    vol.Required(PROJECT_ID): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
})


def setup_platform(hass, config, add_devices, discovery_info=None):
    url = config.get(URL)
    username = config.get(USERNAME)
    password = config.get(PASSWORD)
    project_id = config.get(PROJECT_ID)
    sensor_name = config.get(CONF_NAME)
    add_devices([Chandao("task_" + sensor_name, "task",  url, username, password, project_id)])
    add_devices([Chandao("bug_" + sensor_name, "bug", url, username, password, project_id)])


class Chandao(Entity):
    """Representation of a ha chandao"""

    host = str
    username = str
    password = str
    project_id = str
    session_name = str
    session_id = str
    session = requests.Session
    boundary = str
    type = str
    multipart_header = {}

    def __init__(self, sensor_name: str, type: str, host: str, username: str, password: str, project_id: str):
        self.attributes = {}
        self._state = None
        self._name = sensor_name
        self.type = type
        self.host = host
        self.username = username
        self.password = password
        self.project_id = project_id
        self.session = requests.Session()
        self.boundary = '------WebKitFormBoundaryAmOiBfmEYFBzUOnO'
        self.multipart_header = {'Content-Type': 'multipart/form-data; boundary={0}'.format(self.boundary),
                                 'charset': 'UTF-8'}

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def icon(self):
        """返回mdi图标."""
        return 'mdi:script'

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return self.attributes

    @property
    def unit_of_measurement(self):
        """Return the unit this state is expressed in."""
        return "个"

    def update(self):
        try:
            if self.login():
                if self.type == "task":
                    not_start, start = self.get_task_list()
                    self._state = not_start
                elif self.type == "bug":
                    not_start = self.get_bug_list()
                    self._state = not_start
            else:
                self._state = "登录失败"
                _Log.error("Login Error")
        except ConnectionError:
            _Log.error("Connection Error....")
        except:
            _Log.error("Unknown Error")

    def login(self):
        """login chandao"""
        respond = self.session.get(self.host + '/zentao/api-getsessionid.json')
        if respond.status_code != 200:
            warnings.warn('http error: %d' % respond.status_code)
            return False
        content = respond.json()
        if content['status'] != 'success':
            warnings.warn('获取链接session失败')
            return False
        data = json.loads(content['data'])
        self.session_name = data['sessionName']
        self.session_id = data['sessionID']
        params = {'account': self.username, 'password': self.password}
        respond = self.session.post(self.host + '/zentao/user-login.json?{0}={1}'
                                    .format(self.session_name, self.session_id), params=params)
        if respond.status_code != 200:
            warnings.warn('http error: %d' % respond.status_code)
            return False
        content = respond.json()
        if content['status'] != 'success':
            warnings.warn('登录失败')
            return False
        return True

    def get_task_list(self):
        """get yourself task list"""
        respond = self.session.get(self.host + '/zentao/project-task-{0}-myinvolved.json'.format(self.project_id))
        if respond.status_code != 200:
            warnings.warn('http error: %d' % respond.status_code)
            return False
        data = respond.json()["data"].replace("\\/", "/").encode('utf-8').decode('unicode_escape')
        data_sub = re.sub(r'<[^>]*>', "", data).replace("\n", "")
        data_json = json.loads(data_sub)
        res = data_json["summary"]
        res = re.sub(r'<\/?strong>', "", res).replace(" ", "")
        return re.findall(r'始(.*)，进', res)[0], re.findall(r'中(.*)，总', res)[0]

    def get_bug_list(self):
        """get yourself bug list"""
        respond = self.session.get(self.host + '/zentao/bug-browse-{0}-myinvolved.json'.format(self.project_id))
        if respond.status_code != 200:
            warnings.warn('http error: %d' % respond.status_code)
            return False
        data = respond.json()["data"].replace("\\/", "/").encode('utf-8').decode('unicode_escape')
        data_sub = re.sub(r'<[^>]*>', "", data).replace("\n", "")
        data_json = json.loads(data_sub)
        res = data_json["summary"]
        res = re.sub(r'<\/?strong>', "", res).replace(" ", "")
        return re.findall(r'决(.*)。', res)[0]
