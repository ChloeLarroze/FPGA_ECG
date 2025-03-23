############################
# On-board leds             #
############################
set_property -dict {PACKAGE_PIN R14 IOSTANDARD LVCMOS33} [get_ports {Baud_o[0]}]
set_property -dict {PACKAGE_PIN P14 IOSTANDARD LVCMOS33} [get_ports {Baud_o[1]}]
set_property -dict {PACKAGE_PIN N16 IOSTANDARD LVCMOS33} [get_ports {Baud_o[2]}]
#set_property -dict {PACKAGE_PIN U21 IOSTANDARD LVCMOS33} [get_ports {Baud_o[3]}]

####
# ----------------------------------------------------------------------------
# User PUSH Switches - Bank 35
# ----------------------------------------------------------------------------
set_property -dict {PACKAGE_PIN D19 IOSTANDARD LVCMOS33} [get_ports {Baud_i[0]}]
set_property -dict {PACKAGE_PIN D20 IOSTANDARD LVCMOS33} [get_ports {Baud_i[1]}]
set_property -dict {PACKAGE_PIN L20 IOSTANDARD LVCMOS33} [get_ports {Baud_i[2]}]
#resetb_i
set_property -dict {PACKAGE_PIN L19 IOSTANDARD LVCMOS33} [get_ports reset_i]

## Clock signal 125 MHz

set_property -dict {PACKAGE_PIN H16 IOSTANDARD LVCMOS33} [get_ports clock_i]
#create_clock -add -name sys_clk_pin -period 8.00 -waveform {0 4} [get_ports { clock_i }];

#UART PMODA pin jap1-> RTS jan1-> Tx_o jap2-> Rx_o
set_property -dict {PACKAGE_PIN Y18 IOSTANDARD LVCMOS33} [get_ports RTS_o]
set_property -dict {PACKAGE_PIN Y19 IOSTANDARD LVCMOS33} [get_ports Tx_o]
set_property -dict {PACKAGE_PIN Y16 IOSTANDARD LVCMOS33} [get_ports Rx_i]


set_property MARK_DEBUG true [get_nets {fsm_uart_0/RxData_i[0]}]
set_property MARK_DEBUG true [get_nets {fsm_uart_0/RxData_i[1]}]
set_property MARK_DEBUG true [get_nets {fsm_uart_0/RxData_i[2]}]
set_property MARK_DEBUG true [get_nets {fsm_uart_0/RxData_i[3]}]
set_property MARK_DEBUG true [get_nets {fsm_uart_0/RxData_i[4]}]
set_property MARK_DEBUG true [get_nets {fsm_uart_0/RxData_i[6]}]
set_property MARK_DEBUG true [get_nets {fsm_uart_0/RxData_i[7]}]
set_property MARK_DEBUG true [get_nets fsm_uart_0/RXRdy_i]
set_property MARK_DEBUG false [get_nets <const0>]

create_debug_core u_ila_0 ila
set_property ALL_PROBE_SAME_MU true [get_debug_cores u_ila_0]
set_property ALL_PROBE_SAME_MU_CNT 1 [get_debug_cores u_ila_0]
set_property C_ADV_TRIGGER false [get_debug_cores u_ila_0]
set_property C_DATA_DEPTH 1024 [get_debug_cores u_ila_0]
set_property C_EN_STRG_QUAL false [get_debug_cores u_ila_0]
set_property C_INPUT_PIPE_STAGES 0 [get_debug_cores u_ila_0]
set_property C_TRIGIN_EN false [get_debug_cores u_ila_0]
set_property C_TRIGOUT_EN false [get_debug_cores u_ila_0]
set_property port_width 1 [get_debug_ports u_ila_0/clk]
connect_debug_port u_ila_0/clk [get_nets [list clock_0/inst/clk_out1]]
set_property PROBE_TYPE DATA_AND_TRIGGER [get_debug_ports u_ila_0/probe0]
set_property port_width 8 [get_debug_ports u_ila_0/probe0]
connect_debug_port u_ila_0/probe0 [get_nets [list {fsm_uart_0/RxData_i[0]} {fsm_uart_0/RxData_i[1]} {fsm_uart_0/RxData_i[2]} {fsm_uart_0/RxData_i[3]} {fsm_uart_0/RxData_i[4]} {fsm_uart_0/RxData_i[5]} {fsm_uart_0/RxData_i[6]} {fsm_uart_0/RxData_i[7]}]]
create_debug_port u_ila_0 probe
set_property PROBE_TYPE DATA_AND_TRIGGER [get_debug_ports u_ila_0/probe1]
set_property port_width 1 [get_debug_ports u_ila_0/probe1]
connect_debug_port u_ila_0/probe1 [get_nets [list fsm_uart_0/RXRdy_i]]
set_property C_CLK_INPUT_FREQ_HZ 300000000 [get_debug_cores dbg_hub]
set_property C_ENABLE_CLK_DIVIDER false [get_debug_cores dbg_hub]
set_property C_USER_SCAN_CHAIN 1 [get_debug_cores dbg_hub]
connect_debug_port dbg_hub/clk [get_nets clock_s]
