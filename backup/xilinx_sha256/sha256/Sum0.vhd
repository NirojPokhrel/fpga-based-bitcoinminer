----------------------------------------------------------------------------------
-- Company: 
-- Engineer: 
-- 
-- Create Date:    00:44:31 05/28/2016 
-- Design Name: 
-- Module Name:    Sum0 - Behavioral 
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

-- Uncomment the following library declaration if using
-- arithmetic functions with Signed or Unsigned values
use IEEE.NUMERIC_STD.ALL;

-- Uncomment the following library declaration if instantiating
-- any Xilinx primitives in this code.
--library UNISIM;
--use UNISIM.VComponents.all;

entity Sum0 is
    Port ( x : in  STD_LOGIC_VECTOR (31 downto 0);
           sum0_out : out  STD_LOGIC_VECTOR (31 downto 0));
end Sum0;

architecture Behavioral of Sum0 is

signal temp1, temp2, temp3: STD_LOGIC_VECTOR( 31 downto 0);
begin
	
	temp1 <= std_logic_vector((unsigned(x) srl 2) or (unsigned(x) sll 30));
	temp2 <= std_logic_vector((unsigned(x) srl 13) or (unsigned(x) sll 19));
	temp3 <= std_logic_vector((unsigned(x) srl 22) or (unsigned(x) sll 10));
	sum0_out <= temp1 xor temp2 xor temp3;
end Behavioral;

