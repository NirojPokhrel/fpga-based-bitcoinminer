----------------------------------------------------------------------------------
-- Company: 
-- Engineer: 
-- 
-- Create Date:    00:52:09 05/28/2016 
-- Design Name: 
-- Module Name:    Sig1 - Behavioral 
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

entity Sig1 is
    Port ( x : in  STD_LOGIC_VECTOR (31 downto 0);
           sig1_out : out  STD_LOGIC_VECTOR (31 downto 0));
end Sig1;

architecture Behavioral of Sig1 is

signal temp1, temp2, temp3: STD_LOGIC_VECTOR(31 downto 0);
begin
	
	temp1 <= std_logic_vector((unsigned(x) srl 17) or (unsigned(x) sll 15));
	temp2 <= std_logic_vector((unsigned(x) srl 19) or (unsigned(x) sll 13));
	temp3 <= std_logic_vector((unsigned(x) srl 10));
	
	sig1_out <= temp1 xor temp2 xor temp3;

end Behavioral;

