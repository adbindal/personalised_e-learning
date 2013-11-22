ECHO OFF
TITLE DynamicPAL Algorithm
cls  
::CMD will no longer show us what command it’s executing(cleaner)
ECHO.
ECHO ----------------------------------------------------------------------------
ECHO  Dynamic Learning Path recommendation using Rough Sets and ACO in Elearning
ECHO.									        
ECHO  by:-   Aditya Bindal	                         	                         
ECHO         207/CO/09					 
ECHO         Academic Year (2012 - 2013)                   
ECHO.              						           
ECHO         under the guidence of Mrs. Sushma Hans		
ECHO         (TRF under Prof. Shampa Chakraverty)                              
ECHO ----------------------------------------------------------------------------
ECHO.
ECHO Running DPAL on Current user

:: Outputs tons of ACO simulation into the command prompt
cd ACOnew
python StaticACO.py > ../result_current.txt
cd ..
PAUSE

ECHO Simulating Graphs and presenting output
ECHO.

:: Creates the Graphs from the current output
cd DynamicOPs/ 
python main.py
cd ..
PAUSE

:: Delete the additional files that are created during the Process
del result_current.txt
del Standard.paths

:: Print the Success message!
ECHO Simulation Completed with Success. 
