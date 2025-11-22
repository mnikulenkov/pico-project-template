killall -9 wezterm
killall -9 wezterm-gui
wezterm start -- bash -c "python3 '$(pwd)/project.py' '$(pwd)/config.json'; exec bash"



