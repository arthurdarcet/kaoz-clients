#!/bin/sh
# IRC style

# ^B = bold
IRC_B=$'\x02'

# ^C = color, some clients use ^K because ^C issues SIGINT signal
IRC_K=$'\x03'

# ^O = original
IRC_O=$'\x0F'

# ^R
IRC_R=$'\x16'

# ^_ = underline
IRC_U=$'\x1F'

# Colors
IRC_BLACK="${IRC_K}01"
IRC_NAVY="${IRC_K}02"
IRC_GREEN="${IRC_K}03"
IRC_RED="${IRC_K}04"
IRC_BROWN="${IRC_K}05"
IRC_PURPLE="${IRC_K}06"
IRC_OLIVE="${IRC_K}07"
IRC_YELLOW="${IRC_K}08"
IRC_LIME="${IRC_K}09"
IRC_TEAL="${IRC_K}10"
IRC_AQUA="${IRC_K}11"
IRC_BLUE="${IRC_K}12"
IRC_PINK="${IRC_K}13"
IRC_DARKGRAY="${IRC_K}14"
IRC_LIGHTGRAY="${IRC_K}15"
IRC_WHITE="${IRC_K}16"

# Status
IRC_OK="${IRC_GREEN} OK "
IRC_WARN="${IRC_YELLOW}WARN"
IRC_CRIT="${IRC_RED}CRIT"
IRC_UNKNOWN="${IRC_AQUA} ?? "
