

/* * Copyright (c) 2005 Flanders Interuniversitary Institute for Biotechnology (VIB)
 * *
 * * Authors : Steven Maere, Karel Heymans
 * *
 * * This program is free software; you can redistribute it and/or modify
 * * it under the terms of the GNU General Public License as published by
 * * the Free Software Foundation; either version 2 of the License, or
 * * (at your option) any later version.
 * *
 * * This program is distributed in the hope that it will be useful,
 * * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 
 * * The software and documentation provided hereunder is on an "as is" basis,
 * * and the Flanders Interuniversitary Institute for Biotechnology
 * * has no obligations to provide maintenance, support,
 * * updates, enhancements or modifications.  In no event shall the
 * * Flanders Interuniversitary Institute for Biotechnology
 * * be liable to any party for direct, indirect, special,
 * * incidental or consequential damages, including lost profits, arising
 * * out of the use of this software and its documentation, even if
 * * the Flanders Interuniversitary Institute for Biotechnology
 * * has been advised of the possibility of such damage. See the
 * * GNU General Public License for more details.
 * *
 * * You should have received a copy of the GNU General Public License
 * * along with this program; if not, write to the Free Software
 * * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 * *
 * * Authors: Steven Maere, Karel Heymans
 * * Date: Mar.25.2005
 * * Description: Class that calculates the Hypergeometric probability P(x or more |X,N,n) for given x, X, n, N.    
 **/

import java.io.FileReader;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import cern.jet.stat.*;


/**
 * *****************************************************************
 * HypergeometricDistribution.java    Steven Maere & Karel Heymans (c) March 2005
 * -------------------------------
 * <p/>
 * Class that calculates the Hypergeometric probability P(x or more |X,N,n) for given x, X, n, N.
 * ******************************************************************
 */


public class HypergeometricPvalue {


	
    //private static final int SCALE_RESULT = 100;



    /*--------------------------------------------------------------
    METHODS.
    --------------------------------------------------------------*/
    /**
     * constructor with as arguments strings containing numbers.
     *
     * @param x    number of genes with GO category B in cluster A.
     * @param bigX number of genes in cluster A.
     * @param n    number of genes with GO category B in the whole genome.
     * @param bigN number of genes in whole genome.
     */

	
    /**
     * method that conducts the calculations.
     * P(x or more |X,N,n) = 1 - sum{[C(n,i)*C(N-n, X-i)] / C(N,X)}
     * for i=0 ... x-1
     *
     * @return String with result of calculations.
     */
    public static String calculateHypergDistr(int x, int bigX, int n, int bigN) {
		if(bigN >= 2){
        double sum = 0;
		//mode of distribution, integer division (returns integer <= double result)!
		int mode = (bigX+1)*(n+1)/(bigN+2) ;
		if(x >= mode){
                    int i = x ;
                    while ((bigN - n >= bigX - i) && (i <= Math.min(bigX, n))) {	
                        double pdfi = Math.exp(Gamma.logGamma(n+1)-Gamma.logGamma(i+1)-Gamma.logGamma(n-i+1) + Gamma.logGamma(bigN-n+1)-Gamma.logGamma(bigX-i+1)-Gamma.logGamma(bigN-n-bigX+i+1)- Gamma.logGamma(bigN+1)+Gamma.logGamma(bigX+1)+Gamma.logGamma(bigN-bigX+1)) ;
                        sum = sum+pdfi;
                        i++;
                    }	
		}	
		else{
                    int i = x - 1;
                    while ((bigN - n >= bigX - i) && (i >= 0)) {
			double pdfi = Math.exp(Gamma.logGamma(n+1)-Gamma.logGamma(i+1)-Gamma.logGamma(n-i+1) + Gamma.logGamma(bigN-n+1)-Gamma.logGamma(bigX-i+1)-Gamma.logGamma(bigN-n-bigX+i+1)- Gamma.logGamma(bigN+1)+Gamma.logGamma(bigX+1)+Gamma.logGamma(bigN-bigX+1)) ;
                        sum = sum+pdfi;
                        i--;
                    }	
                    sum = 1-sum;
                }
                return (new Double(sum)).toString();
            }
            else{return (new Double(1)).toString();}
	}	

	public static void main(String[] args)
	{
		
		BufferedReader stdin;
		
		try
		{		
			if(args.length>0)
			{
				stdin=new BufferedReader(new FileReader(args[0]));
			}
			else
			{
				stdin=new BufferedReader(new InputStreamReader(System.in));
			}
		

		while(true)
		{
		
		String line=stdin.readLine();
		
			try
			{
				
				String[] result=line.split("\\s");
				if(result.length!=4)
				{
					System.err.println("_NARGS:"+line);
					continue;
				}
		
				Integer Samt=new Integer(result[0]);
				Integer Sam=new Integer(result[1]);
				Integer Popt=new Integer(result[2]);
				Integer Pop=new Integer(result[3]);
				System.out.println(calculateHypergDistr(Samt,Sam,Popt,Pop));
			}
			
			catch(NumberFormatException nfe)
			{
				System.err.println("_NFE:"+line);
			}
		}
			
		
			
		}
		catch(IOException e)
		{
			
		}
		catch(NullPointerException npe)
		{
			
		}
		
		
		
	
	}
}
		
	    
	
	   
