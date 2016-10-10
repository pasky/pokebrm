This is a brmlab attempt at building a BLE device compatible with the
Pokemon GO Plus wristband.  We are trying to reproduce the handshake
protocol described in:

	https://hackaday.io/project/12680-pokemon-go-plus-diy

As the initial platform, we are using an nRF51 Bluefruit BLEfriend
with UART interface, connected to a Raspberry Pi.

The device is visible, but the handshake doesn't work and we aren't
sure why.
