import evdev

devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
for device in devices:
    print(f'\n-------------------{device.path, device.name, device.phys}--------------')
    # print(device.capabilities())
    for infoCategory, content in device.capabilities(verbose=True).items():
        print(f'\n------------{infoCategory}-----------')
        for info in content: print(info)