#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
; #Warn  ; Enable warnings to assist with detecting common errors.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.


!d::
Send, {Delete}
return

!h::
Send, {Home}
return

!a::
WinActivate, Ableton Project
return

!g::
WinActivate, gen
return

!p::
WinActivate, bgm2 [
return

!/::
Send, {down}
return

