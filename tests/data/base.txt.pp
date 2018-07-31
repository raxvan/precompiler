
//--------------------------------------------------
//#inline
hello world
//--------------------------------------------------
//#run
//--------------------------------------------------
//#inline-run



//--------------------------------------------------
//def undefine test:

x = 0 + 1



//--------------------------------------------------
//define without arguments and ifdef/ifndef

x = 1 + 2


	error



	error




//--------------------------------------------------
//define arguments testing


y = (1,2)
y = (,2)
y = (1,)
y = (,)


(1,2,3)
((1,2),3) //<- characters () are scope begin/end
([1,2],3) //<- characters [] are scope begin/end
({1,2},3) //<- characters {} are scope begin/end



//--------------------------------------------------
//more "complex" argument capture
> world


//--------------------------------------------------
//#inline with define

print("hello world")

//--------------------------------------------------
//colapse token

//foo is:
a+b+c+d

//after colapse

"New A"+b+c+d




//--------------------------------------------------

