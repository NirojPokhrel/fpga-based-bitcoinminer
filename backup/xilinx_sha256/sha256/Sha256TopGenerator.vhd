----------------------------------------------------------------------------------
-- Company: 
-- Engineer: 
-- 
-- Create Date:    12:02:14 05/28/2016 
-- Design Name: 
-- Module Name:    Sha256Generator - Behavioral 
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

use work.PackSha256.all;
-- Uncomment the following library declaration if instantiating
-- any Xilinx primitives in this code.
--library UNISIM;
--use UNISIM.VComponents.all;

entity Sha256Generator is
    Port ( DataIn : in  STD_LOGIC_VECTOR (7 downto 0);
           Clk : in  STD_LOGIC;
           Rst : in  STD_LOGIC;
           DataFinished : in  STD_LOGIC;
			  OutputReady: out STD_LOGIC;
           Hout : out  STD_LOGIC_VECTOR (255 downto 0));
end Sha256Generator;

architecture Behavioral of Sha256Generator is
signal msg: M_Array;
type acum is array(0 to 511) of STD_LOGIC_VECTOR(7 downto 0);
signal data_acum: acum;
signal datafilled, start_processing, output_ready: STD_LOGIC;

begin

ACCUMULATE:
process(clk)
	variable cnt := integer := 0;
	datafilled <='0';
begin
	if clk'event and clk = '1' then
		cnt := cnt + 1;
		data_acum(cnt) <= DataIn;
		if cnt = 512 then
			datafilled <= '1';
			cnt := 0;
		end if;
	end if;
end process;

DATACOPY:
process(datafilled)
	start_processing <= '0';
begin
	if datafilled = '1' then
	for i in 0 to 63 loop
		msg(i)(31 downto 24) <= data_acum(i*4);
		msg(i)(23 downto 16) <= data_acum(i*4+1);
		msg(i)(15 downto 8) <= data_acum(i*4+2);
		msg(i)(7 downto 0) <= data_acum(i*4+3);
	end loop;
	end if;
	start_processing <='1';
end process;

GENERATE_OUTPUT:
process(output_ready)
begin
end process;


end Behavioral;

