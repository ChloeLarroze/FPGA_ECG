set_property SRC_FILE_INFO {cfile:C:/Users/eleves/new_fpga_25mars/new_fpga_25mars.srcs/constrs_1/imports/new/uart_test.xdc rfile:../../../new_fpga_25mars.srcs/constrs_1/imports/new/uart_test.xdc id:1} [current_design]
set_property src_info {type:XDC file:1 line:4 export:INPUT save:INPUT read:READ} [current_design]
set_property -dict {PACKAGE_PIN R14 IOSTANDARD LVCMOS33} [get_ports {Baud_o[0]}]
set_property src_info {type:XDC file:1 line:5 export:INPUT save:INPUT read:READ} [current_design]
set_property -dict {PACKAGE_PIN P14 IOSTANDARD LVCMOS33} [get_ports {Baud_o[1]}]
set_property src_info {type:XDC file:1 line:6 export:INPUT save:INPUT read:READ} [current_design]
set_property -dict {PACKAGE_PIN N16 IOSTANDARD LVCMOS33} [get_ports {Baud_o[2]}]
set_property src_info {type:XDC file:1 line:13 export:INPUT save:INPUT read:READ} [current_design]
set_property -dict {PACKAGE_PIN D19 IOSTANDARD LVCMOS33} [get_ports {Baud_i[0]}];  # "SW0"
set_property src_info {type:XDC file:1 line:14 export:INPUT save:INPUT read:READ} [current_design]
set_property -dict {PACKAGE_PIN D20 IOSTANDARD LVCMOS33} [get_ports {Baud_i[1]}];  # "SW1"
set_property src_info {type:XDC file:1 line:15 export:INPUT save:INPUT read:READ} [current_design]
set_property -dict {PACKAGE_PIN L20 IOSTANDARD LVCMOS33} [get_ports {Baud_i[2]}];  # "SW2"
set_property src_info {type:XDC file:1 line:17 export:INPUT save:INPUT read:READ} [current_design]
set_property -dict {PACKAGE_PIN L19 IOSTANDARD LVCMOS33} [get_ports {reset_i}]
set_property src_info {type:XDC file:1 line:21 export:INPUT save:INPUT read:READ} [current_design]
set_property -dict { PACKAGE_PIN H16   IOSTANDARD LVCMOS33 } [get_ports { clock_i }]; #IO_L13P_T2_MRCC_35 Sch=sysclk
set_property src_info {type:XDC file:1 line:25 export:INPUT save:INPUT read:READ} [current_design]
set_property -dict { PACKAGE_PIN Y18   IOSTANDARD LVCMOS33 } [get_ports { RTS_o }]; #IO_L17P_T2_34 Sch=ja_p[1]
set_property src_info {type:XDC file:1 line:26 export:INPUT save:INPUT read:READ} [current_design]
set_property -dict { PACKAGE_PIN Y19   IOSTANDARD LVCMOS33 } [get_ports { Tx_o }]; #IO_L17N_T2_34 Sch=ja_n[1]
set_property src_info {type:XDC file:1 line:27 export:INPUT save:INPUT read:READ} [current_design]
set_property -dict { PACKAGE_PIN Y16   IOSTANDARD LVCMOS33 } [get_ports { Rx_i }]; #IO_L7P_T1_34 Sch=ja_p[2]
