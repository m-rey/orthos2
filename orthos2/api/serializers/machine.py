from orthos2.data.models import Machine, RemotePower
from rest_framework import serializers

from .annotation import AnnotationSerializer
from .installation import InstallationSerializer
from .networkinterface import NetworkInterfaceSerializer


class NetworkInterfaceListingField(NetworkInterfaceSerializer):

    def to_representation(self, networkinterface):
        result = {}

        for name, field in self.fields.items():
            value = getattr(networkinterface, name)
            result[name] = {'label': field.label, 'value': value}

        return result


class InstallationListingField(InstallationSerializer):

    def to_representation(self, installation):
        result = {}

        for name, field in self.fields.items():
            value = getattr(installation, name)
            result[name] = {'label': field.label, 'value': value}

        return result


class AnnotationListingField(AnnotationSerializer):

    def to_representation(self, annotation):
        result = {}

        for name, field in self.fields.items():
            value = getattr(annotation, str(name))
            if name == 'reporter':
                if value:
                    value = value.username
                else:
                    value = 'unknown'
            result[name] = {'label': field.label, 'value': value}

        return result


class MachineSerializer(serializers.ModelSerializer):

    enclosure = serializers.StringRelatedField()

    system = serializers.StringRelatedField()

    architecture = serializers.StringRelatedField()

    networkinterfaces = NetworkInterfaceListingField(many=True)

    reserved_by = serializers.StringRelatedField()

    installations = InstallationListingField(many=True)

    annotations = AnnotationListingField(many=True)

    status_ipv4 = serializers.SerializerMethodField()
    status_ipv6 = serializers.SerializerMethodField()

    class Meta:
        model = Machine
        fields = (
            'fqdn',
            'ipv4',
            'ipv6',
            'comment',
            'group',
            'serial_number',
            'product_code',
            'enclosure',
            'nda',
            'system',
            'architecture',
            'networkinterfaces',
            'installations',
            'annotations',
            'status_ipv6',
            'status_ipv4',
            'status_ssh',
            'status_login',
            'status_abuild',
            'reserved_by',
            'reserved_reason',
            'reserved_at',
            'reserved_until',
            'cpu_model',
            'cpu_id',
            'cpu_cores',
            'cpu_physical',
            'cpu_threads',
            'cpu_flags',
            'ram_amount',
            'serial_type',
            'serial_management_bmc',
            'serial_cscreen_server',
            'serial_console_server',
            'serial_device',
            'serial_port',
            'serial_command',
            'serial_comment',
            'serial_baud_rate',
            'serial_kernel_device',
            'power_type',
            'power_management_bmc',
            'power_host',
            'power_port',
            'power_device',
            'power_comment',
            'location_room',
            'location_rack',
            'location_rack_position'
        )

    serial_type = serializers.CharField(source='serialconsole.type.name')
    serial_cscreen_server = serializers.CharField(source='serialconsole.cscreen_server')
    serial_management_bmc = serializers.CharField(
        source='serialconsole.management_bmc'
    )
    serial_console_server = serializers.CharField(source='serialconsole.console_server')
    serial_device = serializers.CharField(source='serialconsole.device')
    serial_port = serializers.IntegerField(source='serialconsole.port')
    serial_command = serializers.CharField(source='serialconsole.command')
    serial_comment = serializers.CharField(source='serialconsole.comment')
    serial_baud_rate = serializers.IntegerField(source='serialconsole.baud_rate')
    serial_kernel_device = serializers.IntegerField(source='serialconsole.kernel_device')

    power_type = serializers.CharField(source='remotepower.type')
    power_management_bmc = serializers.CharField(
        source='remotepower.management_bmc'
    )
    power_host = serializers.CharField(source='remotepower.remote_power_device')
    power_port = serializers.IntegerField(source='remotepower.port')
    power_device = serializers.CharField(source='remotepower.device')
    power_comment = serializers.CharField(source='remotepower.comment')

    location_room = serializers.CharField(source='enclosure.location_room')
    location_rack = serializers.CharField(source='enclosure.location_rack')
    location_rack_position = serializers.CharField(source='enclosure.location_rack_position')

    group = serializers.CharField(source='group.name')

    def __init__(self, machine, *args, **kwargs):
        super(MachineSerializer, self).__init__(machine, *args, **kwargs)
        if  not hasattr(machine, 'group') or not machine.group:
            self.fields.pop('group')

    @property
    def data_info(self):
        result = {}

        # copy dictionary for further manipulation
        data = self.data

        # add keys to exclude list which shouldn't be displayed if value is empty...
        exclude = []
        for key in self.fields.keys():
            if key.startswith('serial_') or key.startswith('power_'):
                exclude.append(key)

        exclude.remove('serial_type')
        exclude.remove('power_type')

        for name, field in self.fields.items():
            if name == 'ipv4':
                field.label = 'IPv4'
            if name == 'ipv6':
                field.label = 'IPv6'
            if name == 'status_ipv4':
                field.label = 'Status IPv4'
            if name == 'status_ipv6':
                field.label = 'Status IPv6'
            if name == 'power_type' and data[name]:
                data[name] = RemotePower.Type.to_str(data[name])

            # ... do not add label/values if in exclude list
            if (name in exclude) and (data[name] is None):
                continue

            result[name] = {'label': field.label, 'value': data[name]}

        return result

    def get_status_ipv4(self, obj):
        return obj.get_status_ipv4_display()

    def get_status_ipv6(self, obj):
        return obj.get_status_ipv6_display()
