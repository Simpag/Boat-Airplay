## Install
Make ``wifi_manager.sh`` executable:
```
# chmod +x wifi_manager.sh
```

Copy ``wifi-manager.service`` to ``/etc/systemd/system/``

To enable the service, run the following: 

* `# systemctl start wifi-manager.service` to run the script now.
* `# systemctl enable wifi-manager.service` to set the script to run every boot.