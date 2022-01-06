cmake_minimum_required(VERSION 2.8)
PROJECT(virtualgps NONE)

set (VERSION_MAJOR 1)
set (VERSION_MINOR 1)
set (VERSION_RELEASE 1)

set(BIN_INSTALL_DIR "/usr/bin")
set(CONFIG_INSTALL_DIR "/etc")
set(MENU_INSTALL_DIR "/usr/share/applications")

if (${CMAKE_SYSTEM_NAME} MATCHES "Linux")
	install(FILES ${CMAKE_CURRENT_SOURCE_DIR}/virtualgps.py DESTINATION ${BIN_INSTALL_DIR})
	install(FILES ${CMAKE_CURRENT_SOURCE_DIR}/setlocation.sh DESTINATION ${BIN_INSTALL_DIR})
	install(FILES ${CMAKE_CURRENT_SOURCE_DIR}/location.conf DESTINATION ${CONFIG_INSTALL_DIR})
	install(FILES ${CMAKE_CURRENT_SOURCE_DIR}/virtualgps.service DESTINATION ${CONFIG_INSTALL_DIR}/systemd/system)
	install(FILES ${CMAKE_CURRENT_SOURCE_DIR}/setlocation.desktop DESTINATION ${MENU_INSTALL_DIR})
endif()
