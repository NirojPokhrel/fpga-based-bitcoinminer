----------------------------------------------------------------------------------
-- Company: 
-- Engineer: 
-- 
-- Create Date:    09:46:00 05/28/2016 
-- Design Name: 
-- Module Name:    Sha256Compression - Behavioral 
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

entity Sha256Compression is
    Port ( Hin : in  H_Array;
           Msg : in  M_Array;
           Hout : out  H_Array);
end Sha256Compression;

architecture Behavioral of Sha256Compression is

component Sum0 is
    Port ( x : in  STD_LOGIC_VECTOR (31 downto 0);
           sum0_out : out  STD_LOGIC_VECTOR (31 downto 0));
end component;

component Sum1 is
    Port ( x : in  STD_LOGIC_VECTOR (31 downto 0);
           sum1_out : out  STD_LOGIC_VECTOR (31 downto 0));
end component;

component Maj is
    Port ( x : in  STD_LOGIC_VECTOR (31 downto 0);
           y : in  STD_LOGIC_VECTOR (31 downto 0);
           z : in  STD_LOGIC_VECTOR (31 downto 0);
           maj_out : out  STD_LOGIC_VECTOR (31 downto 0));
end component;

component Ch is
    Port ( x : in  STD_LOGIC_VECTOR (31 downto 0);
           y : in  STD_LOGIC_VECTOR (31 downto 0);
           z : in  STD_LOGIC_VECTOR (31 downto 0);
           ch_out : out  STD_LOGIC_VECTOR (31 downto 0));
end component;

component Generate_W is
    Port ( msg : in  M_Array;
           w : out  W_Array);
end component;


signal a, b, c, d, e, f, g, h, T1, T2: STD_LOGIC_VECTOR( 31 downto 0);
signal temp1, temp2, temp3, temp4: STD_LOGIC_VECTOR( 31 downto 0);
signal w: W_Array;
signal k: W_Array := 
	(
		0 => "01000010100010100010111110011000",
		1 => "01110001001101110100010010010001",
		2 => "10110101110000001111101111001111",
		3 => "11101001101101011101101110100101",
		4 => "00111001010101101100001001011011",
		5 => "01011001111100010001000111110001",
		6 => "10010010001111111000001010100100",
		7 => "10101011000111000101111011010101",
		8 => "11011000000001111010101010011000",
		9 => "00010010100000110101101100000001",
		10 => "00100100001100011000010110111110",
		11 => "01010101000011000111110111000011",
		12 => "01110010101111100101110101110100",
		13 => "10000000110111101011000111111110",
		14 => "10011011110111000000011010100111",
		15 => "11000001100110111111000101110100",
		16 => "11100100100110110110100111000001",
		17 => "11101111101111100100011110000110",
		18 => "00001111110000011001110111000110",
		19 => "00100100000011001010000111001100",
		20 => "00101101111010010010110001101111",
		21 => "01001010011101001000010010101010",
		22 => "01011100101100001010100111011100",
		23 => "01110110111110011000100011011010",
		24 => "10011000001111100101000101010010",
		25 => "10101000001100011100011001101101",
		26 => "10110000000000110010011111001000",
		27 => "10111111010110010111111111000111",
		28 => "11000110111000000000101111110011",
		29 => "11010101101001111001000101000111",
		30 => "00000110110010100110001101010001",
		31 => "00010100001010010010100101100111",
		32 => "00100111101101110000101010000101",
		33 => "00101110000110110010000100111000",
		34 => "01001101001011000110110111111100",
		35 => "01010011001110000000110100010011",
		36 => "01100101000010100111001101010100",
		37 => "01110110011010100000101010111011",
		38 => "10000001110000101100100100101110",
		39 => "10010010011100100010110010000101",
		40 => "10100010101111111110100010100001",
		41 => "10101000000110100110011001001011",
		42 => "11000010010010111000101101110000",
		43 => "11000111011011000101000110100011",
		44 => "11010001100100101110100000011001",
		45 => "11010110100110010000011000100100",
		46 => "11110100000011100011010110000101",
		47 => "00010000011010101010000001110000",
		48 => "00011001101001001100000100010110",
		49 => "00011110001101110110110000001000",
		50 => "00100111010010000111011101001100",
		51 => "00110100101100001011110010110101",
		52 => "00111001000111000000110010110011",
		53 => "01001110110110001010101001001010",
		54 => "01011011100111001100101001001111",
		55 => "01101000001011100110111111110011",
		56 => "01110100100011111000001011101110",
		57 => "01111000101001010110001101101111",
		58 => "10000100110010000111100000010100",
		59 => "10001100110001110000001000001000",
		60 => "10010000101111101111111111111010",
		61 => "10100100010100000110110011101011",
		62 => "10111110111110011010001111110111",
		63 => "11000110011100010111100011110010"
);		
begin
	u0: Generate_W port map( msg=>Msg, w=>w);
	a <= Hin(0);
	b <= Hin(1);
	c <= Hin(2);
	d <= Hin(3);
	e <= Hin(4);
	f <= Hin(5);
	g <= Hin(6);
	h <= Hin(7);
INIT:
	for i in 0 to 63 generate
		u1: Sum0 port map( x=>a, sum0_out=>temp1);
		u2: Sum1 port map( x=>e, sum1_out=>temp2);
		u3: Maj port map( x=>e, y=>f, z=>g, maj_out=>temp3);
		u4: Ch port map( x=>a, y=>b, z=>c, ch_out=>temp4);
		
		T1 <= std_logic_vector(unsigned(h) + unsigned(temp2) + unsigned(temp4) + 
										unsigned(w(i)) + unsigned(k(i))); --TODO: 
		T2 <= std_logic_vector(unsigned(temp1) + unsigned(temp3));
		h <= g;
		g <= f;
		f <= e;
		e <= std_logic_vector(unsigned(d) + unsigned(T1));
		d <= c;
		c <= b;
		b <= a;
		a <= std_logic_vector(unsigned(T1) + unsigned(T2));
	end generate INIT;

	Hout(0) <= std_logic_vector(unsigned(a) + unsigned(Hin(0)));
	Hout(1) <= std_logic_vector(unsigned(b) + unsigned(Hin(1)));
	Hout(2) <= std_logic_vector(unsigned(c) + unsigned(Hin(2)));
	Hout(3) <= std_logic_vector(unsigned(d) + unsigned(Hin(3)));
	Hout(4) <= std_logic_vector(unsigned(e) + unsigned(Hin(4)));
	Hout(5) <= std_logic_vector(unsigned(f) + unsigned(Hin(5)));
	Hout(6) <= std_logic_vector(unsigned(g) + unsigned(Hin(6)));
	Hout(7) <= std_logic_vector(unsigned(h) + unsigned(Hin(7)));
	
end Behavioral;

