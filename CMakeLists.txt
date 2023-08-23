cmake_minimum_required(VERSION 2.8)
PROJECT(virtualgps NONE)

set (VERSION_MAJOR 1)
set (VERSION_MINOR 2)
set (VERSION_RELEASE 0)

set(BIN_INSTALL_DIR "/usr/bin")
set(CONFIG_INSTALL_DIR "/etc")

if (${CMAKE_SYSTEM_NAME} MATCHES "Linux")
	install(FILES ${CMAKE_CURRENT_SOURCE_DIR}/virtualgps.py DESTINATION ${BIN_INSTALL_DIR})
	install(FILES ${CMAKE_CURRENT_SOURCE_DIR}/virtualgps.conf DESTINATION ${CONFIG_INSTALL_DIR})
	install(FILES ${CMAKE_CURRENT_SOURCE_DIR}/virtualgps.service DESTINATION ${CONFIG_INSTALL_DIR}/systemd/system)
endif()
