----------------------------------------------------------------------------------
-- Company: 
-- Engineer: 
-- 
-- Create Date:    00:48:29 05/28/2016 
-- Design Name: 
-- Module Name:    Sum1 - Behavioral 
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

entity Sum1 is
    Port ( x : in  STD_LOGIC_VECTOR (31 downto 0);
           sum1_out : out  STD_LOGIC_VECTOR (31 downto 0));
end Sum1;

architecture Behavioral of Sum1 is

signal temp1, temp2, temp3: STD_LOGIC_VECTOR( 31 downto 0);
begin

	temp1 <= std_logic_vector((unsigned(x) srl 6) or (unsigned(x) sll 26));
	temp2 <= std_logic_vector((unsigned(x) srl 11) or (unsigned(x) sll 21));
	temp3 <= std_logic_vector((unsigned(x) srl 25) or (unsigned(x) sll 7));
	
	sum1_out <= temp1 xor temp2 xor temp3;

end Behavioral;

