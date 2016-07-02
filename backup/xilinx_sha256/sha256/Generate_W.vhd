----------------------------------------------------------------------------------
-- Company: 
-- Engineer: 
-- 
-- Create Date:    09:05:19 05/28/2016 
-- Design Name: 
-- Module Name:    Generate_W - Behavioral 
-- Project Name: 
-- Target Devices: 
-- Tool versions: 
-- Description: 
--
-- Dependencies: 
--
-- Revision: 
-- Revision 0.01 - File Created
-- Additional Comments: 
--
----------------------------------------------------------------------------------
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

use work.PackSha256.all;

-- Uncomment the following library declaration if using
-- arithmetic functions with Signed or Unsigned values
use IEEE.NUMERIC_STD.ALL;

-- Uncomment the following library declaration if instantiating
-- any Xilinx primitives in this code.
--library UNISIM;
--use UNISIM.VComponents.all;

entity Generate_W is
    Port ( msg : in  M_Array;
           w : out  W_Array);
end Generate_W;

architecture Behavioral of Generate_W is

component Sig0 is
    Port ( x : in  STD_LOGIC_VECTOR (31 downto 0);
           sig0_out : out  STD_LOGIC_VECTOR (31 downto 0));
end component;

component Sig1 is
    Port ( x : in  STD_LOGIC_VECTOR (31 downto 0);
           sig1_out : out  STD_LOGIC_VECTOR (31 downto 0));
end component;

signal temp1, temp2: StD_LOGIC_VECTOR( 31 downto 0);
signal w_temp: W_Array;
begin

--TODO: Make Sure that msg is in proper format otherwise we will need to change this
INIT:
	for i in 0 to 15 generate
		w_temp(i) <= msg(i);
	end generate INIT;
MAIN_LOOP:
	for i in 16 to 63 generate
		u0: Sig0 PORT MAP (x=>w_temp(i-15), sig0_out=>temp1);
		u1: Sig1 PORT MAP (x=>w_temp(i-2), sig1_out=>temp2);
		w_temp(i) <= std_logic_vector( unsigned(temp1) + unsigned(temp2) + 
											  unsigned(w_temp(i-7))+unsigned(w_temp(i-16)));
	end generate MAIN_LOOP;

	w <= w_temp;
end Behavioral;

