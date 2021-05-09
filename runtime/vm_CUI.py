import re
import sys
import os
import time
import difflib
from multiprocessing import Process, Value, Array, Lock
codes=[]
com=[]
opr=[]
stack=[]
rstack=[]
temp=[]
ldata=[]
rdata=[]
top=-1
count_pc=0
parflag=0
args=sys.argv

#push:
def push(a,stack,top):
    stack.append(a)
    return top+1

#pop1:
def pop1(stack,top):
    #t=stack[top-1]
    t=stack.pop()
    return (t,top-1)

"""
def phi(opr):
    f=open('proc_table.txt',mode='r')
    tables=f.read()
    for i in range(0,len(tables),9):
        t1=tables[i:i+3]
        s1=re.search(r'\d+',t1)
        if (int)(s1.group()) == (int)(opr) :
            t2=tables[i+3:i+8]
            s2=re.search(r'\d+',t2)
            return (int)(s2.group())
"""

def search_table(opr,process_path):
    with open("variable_table.txt",'r') as f:
            variable_table=f.read().split('\n')
    t=0
    address=0
    for i in range(0,len(variable_table)-1,1):
        s=re.search(r'\d+',variable_table[i])
        if s.group()==(str)(opr):
            s2=re.search(r'([a-z](\d+).)+E',variable_table[i])
            match_count=0
            temp_path=s2.group()
            if len(process_path)>=len(temp_path):
                for j in reversed(range(0,len(s2.group()),1)):
                    if process_path[j]==temp_path[j]:
                        match_count=match_count+1
                    else:
                        break
                if match_count>=t:
                    address=i
                    t=match_count
    return address
    

def executedcommand(stack,rstack,lstack,com,opr,pc,pre,top,rtop,ltop,address,value,tablecount,variable_region,lock,process_number,process_path,count_pc,process_count,terminate_flag,flag_number):
    if com[pc]==1:#push
        top=push(opr[pc],stack,top)
        pre=pc
        return (pc+1,pre,stack,top,rtop,tablecount,process_path)
    elif com[pc]==2:#load
        value.acquire()
        c=value[search_table(opr[pc],process_path)]
        value.release()
        top=push(c,stack,top)
        pre=pc
        return (pc+1,pre,stack,top,rtop,tablecount,process_path)
    elif com[pc]==3:#store
        value.acquire()
        """
        rstack[rtop.value]=(value[opr[pc]])
        rstack[rtop.value+1]=0
        """
        with open("value_stack.txt",'a') as f:
            f.write(str(value[search_table(opr[pc],process_path)])+' '+str(process_number)+'.'+process_path+'\n')
        f.close()
        rtop.value=rtop.value+2
        (value[search_table(opr[pc],process_path)],top)=pop1(stack,top)
        value.release()
        pre=pc
        return (pc+1,pre,stack,top,rtop,tablecount,process_path)
    elif com[pc]==4:#jpc
        (c,top)=pop1(stack,top)
        if c==1:
            pre=pc
            pc=opr[pc]-2
        return (pc+1,pre,stack,top,rtop,tablecount,process_path)
    elif com[pc]==5:#jmp
        pre=pc
        pc=opr[pc]-2
        return (pc+1,pre,stack,top,rtop,tablecount,process_path)
    elif com[pc]==6:#op
        if (opr[pc])==0:#'+'
            (c,top)=pop1(stack,top)
            (d,top)=pop1(stack,top)
            top=push(c+d,stack,top)
        elif (opr[pc])==1:#'*'
            (c,top)=pop1(stack,top)
            (d,top)=pop1(stack,top)
            top=push(c*d,stack,top)
        elif opr[pc]==2:#'-'
            (c,top)=pop1(stack,top)
            (d,top)=pop1(stack,top)
            top=push(d-c,stack,top)
        elif opr[pc]==3:#'>'
            (c,top)=pop1(stack,top)
            (d,top)=pop1(stack,top)
            if d>c:
                top=push(1,stack,top)
            else:
                top=push(0,stack,top)
        elif opr[pc]==4:#'=='
            (c,top)=pop1(stack,top)
            (d,top)=pop1(stack,top)
            if d==c:
                top=push(1,stack,top)
            else:
                top=push(0,stack,top)
        pre=pc
        return (pc+1,pre,stack,top,rtop,tablecount,process_path)
    elif com[pc]==7:#label
        if args[2]=='f':
            """
            lstack[ltop.value]=(pre)
            lstack[ltop.value+1]=0
            """
            with open("label_stack.txt",'a') as f:
                f.write(str(count_pc-pre)+' '+str(process_number)+'.'+process_path+'\n')
            f.close()
            ltop.value = ltop.value+2
        pre=pc
        return (pc+1,pre,stack,top,rtop,tablecount,process_path)
    elif com[pc]==8:#rjmp
        """
        ltop.value=ltop.value-1
        pc=int(lstack[ltop.value])
        pc=pc-2
        ltop.value=ltop.value-1
        """
        a=int(lstack[ltop.value])-1
        ltop.value=ltop.value-2
        pre=pc
        return (a,pre,stack,top,rtop,tablecount,process_path)
    elif com[pc]==9:#restore
        value[search_table(opr[pc],process_path)]=int(rstack[rtop.value])
        rtop.value=rtop.value-2
        pre=pc
        return (pc+1,pre,stack,top,rtop,tablecount,process_path)
    elif com[pc]==0:#nop
        pre=pc
        return (pc+1,pre,stack,top,rtop,tablecount,process_path)
    elif com[pc]==10:#par
        #if opr[pc]==1:
        #    terminate_flag[flag_number]=1
        #    print(str(flag_number))
        pre=pc
        return (pc+1,pre,stack,top,rtop,tablecount,process_path)
    elif com[pc]==11:#alloc
        #top=push(0,stack,top)
        if args[2]=='f':
            value[tablecount.value] = 0
            variable_region.append(0)
            with open("variable_table.txt",'a') as f:
                f.write(str(opr[pc])+'.'+process_path+'      0\n')
            tablecount.value=tablecount.value+1
        elif args[2]=='b':
            variable_path=search_table(opr[pc],process_path)
            variable_region.append(0)
            with open("variable_table.txt",'r') as f:
                variable_table=f.read().split('\n')
            s=re.search(r'\s(-)?(\d+)',variable_table[variable_path])
            variable_value=int(s.group().strip(' '))
            value[search_table(opr[pc],process_path)]=variable_value
            tablecount.value=tablecount.value+1
        pre=pc
        return (pc+1,pre,stack,top,rtop,tablecount,process_path)
    elif com[pc]==12:#free
        #a=value.pop()
        table_address=search_table(opr[pc],process_path)
        with open("variable_table.txt",'r+') as f:
            buf=f.read()
            line_flag=0
            value_flag=0
            for i in range(0,len(buf),1):
                if line_flag==table_address:
                    if value_flag==1:
                        seek_address=i
                        value_flag=2
                    elif buf[i]==' ' and value_flag==0:
                        value_flag=1
                    elif buf[i]=='\n':
                        seekend_address=i
                        break
                if buf[i]=='\n':
                    line_flag=line_flag+1
            #print(str(seek_address))
            f.seek(seek_address+table_address)
            f.write(str(value[table_address]).rjust(6)+'\n')
        f.close()
        value[table_address]=0
        pre=pc
        variable_region[opr[pc]] = value[opr[pc]]
        return (pc+1,pre,stack,top,rtop,tablecount,process_path)
    elif com[pc]==13:#proc
        if args[2]=='f':
            #lstack[ltop.value]=(pre)
            #lstack[ltop.value+1]=0
            with open("label_stack.txt",'a') as f:
                f.write(str(count_pc-pre)+' '+str(process_number)+'.'+process_path+'\n')
            f.close()
            #ltop.value = ltop.value+2
            push(pre+1,stack,top)
        pre=pc
        #add_path(opr)
        process_path='p'+str(opr[pc])+'.'+process_path
        return (pc+1,pre,stack,top,rtop,tablecount,process_path)
    elif com[pc]==14:#ret
        if args[2]=='f':
            (c,top) = pop1(stack,top)
        elif args[2]=='b':
            #ltop.value=ltop.value-1
            #pc=int(lstack[ltop.value])
            #pc=pc-2
            #ltop.value=ltop.value-1
            c=int(lstack[ltop.value])-1
            ltop.value=ltop.value-2
        #cut_path(opr)
        for i in range(0,len(process_path),1):
            if process_path[i] == '.':
                process_path=process_path[i+1:len(process_path)]
                break
        pre=pc
        return (c,pre,stack,top,rtop,tablecount,process_path)
    elif com[pc]==15:#block
        #add_path(opr)
        if com[pc+3]==16 and (com[pc+1]==5 or com[pc+1]==8):
            process_path='c'+str(opr[pc])+'.'+process_path
        else:
            process_path='b'+str(opr[pc])+'.'+process_path
        pre=pc
        return (pc+1,pre,stack,top,rtop,tablecount,process_path)
    elif com[pc]==16:#end
        #cut_path(opr)
        for i in range(0,len(process_path),1):
            if process_path[i] == '.':
                process_path=process_path[i+1:len(process_path)]
                break
        pre=pc
        return (pc+1,pre,stack,top,rtop,tablecount,process_path)
    elif com[pc]==17:#fork
        if args[2]=='f':
            lock.release()
            process={}
            start_process_count = process_count.value
            already_terminate = {}
            f=open('a'+(str)(opr[pc])+'.txt',mode='r')
            tables=f.read()
            for i in range(0,len(tables),10):
                t1=tables[i:i+4]
                s1=re.search(r'\d+',t1)
                t2=tables[i+5:i+9]
                s2=re.search(r'\d+',t2)
                terminate_flag[process_count.value]=0
                #already_terminate[i]=0
                process[process_count.value]=Process(target=execution,args=(com,opr,(int)(s1.group()),(int)(s2.group()),count_pc,stack,address,value,tablecount,rstack,lstack,rtop,ltop,0,variable_region,lock,process_number + '.' + str(process_count.value-start_process_count+1),process_path,process_count,terminate_flag,process_count.value))
                process_count.value=process_count.value+1
            end_process_count = process_count.value
            for i in range(start_process_count,process_count.value,1):
                process[i].start()
            terminate_count=0
            for i in range(0,100,1):
                already_terminate[i]=0
            while True:
                #if flag_number==7:
                #    if process[9].is_alive():
                ##        print("alive")
                #    else:
                #        print("dead")
                #print(str(flag_number))
                for i in range(start_process_count,end_process_count,1):
                    #print(str(flag_number))
                    if terminate_flag[i]==1 and already_terminate[i]==0:
                        #lock.acquire()
                        process[i].terminate()
                        process[i].join()
                        already_terminate[i]=1
                        terminate_count=terminate_count+1
                        #print("!!!!process"+str(i)+"terminated!!!!!!!")
                        if not process[i].is_alive():
                            process[i].join()
                            #print("join process successfully")
                        #for i in range(start_process_count,end_process_count,1):
                        #    if process[i].is_alive() :
                        #        print("++++++++++++++process"+str(i)+" is alive ++++++++++++++")
                        #lock.release()
                if terminate_count==end_process_count-start_process_count:
                    pre=pc
                    #print("-------------process merge---------- now process is "+str(flag_number)+"next pc "+str(int(s2.group())))
                    lock.acquire()
                    return (int(s2.group()),pre,stack,top,rtop,tablecount,process_path)
            #for i in range(start_process_count,end_process_count,1):
            #    process[i].join()
            #a=int(s2.group())
        elif args[2]=='b':
            lock.release()
            process={}
            start_process_count = process_count.value
            f=open('a'+(str)(opr[pc])+'.txt',mode='r')
            already_terminate = {}
            tables=f.read()
            tables_process_number = int(len(tables)/10)
            print(str(tables_process_number))
            #for i in range(0,len(tables),10):
            #    if tables[i]=='\n':
            #        process_count=process_count+1
            #process_count.value-start_process_count+1
            for i in range(0,len(tables),10):
                t1=tables[i:i+4]
                s1=re.search(r'\d+',t1)
                t2=tables[i+5:i+9]
                s2=re.search(r'\d+',t2)
                terminate_flag[process_count.value]=0
                #print("process " +str(process_count.value-start_process_count+1)+" is generated.")
                #print("process "+str(flag_number)+" generate flag_number is "+str(process_count.value))
                process[process_count.value]=Process(target=execution,args=(com,opr,count_pc-(int)(s2.group())+1,count_pc-(int)(s1.group())+1,count_pc,stack,address,value,tablecount,rstack,lstack,rtop,ltop,0,variable_region,lock,process_number + '.' + str(process_count.value-start_process_count+1),process_path,process_count,terminate_flag,process_count.value))
                process_count.value=process_count.value+1
            end_process_count = process_count.value
            for i in range(start_process_count,process_count.value,1):
                process[i].start()
            terminate_count=0
            for i in range(0,100,1):
                already_terminate[i]=0
            t3=tables[0:0+4]
            s3=re.search(r'\d+',t3)
            while True:
                #if flag_number==7:
                #    if process[9].is_alive():
                ##        print("alive")
                #    else:
                #        print("dead")
                #print(str(flag_number))
                for i in range(start_process_count,end_process_count,1):
                    #print(str(flag_number))
                    if terminate_flag[i]==1 and already_terminate[i]==0:
                        #lock.acquire()
                        process[i].terminate()
                        process[i].join()
                        already_terminate[i]=1
                        terminate_count=terminate_count+1
                        #print("!!!!process"+str(i)+"terminated!!!!!!!")
                        if not process[i].is_alive():
                            process[i].join()
                            #print("join process successfully")
                        #for i in range(start_process_count,end_process_count,1):
                        #    if process[i].is_alive() :
                        #        print("++++++++++++++process"+str(i)+" is alive ++++++++++++++")
                        #lock.release()
                if terminate_count==end_process_count-start_process_count:
                    pre=pc
                    #print("-------------process merge---------- now process is "+str(flag_number)+"next pc "+str(int(s2.group())))
                    lock.acquire()
                    return (count_pc-int(s3.group())+1,pre,stack,top,rtop,tablecount,process_path)
            for i in range(start_process_count,process_count.value,1):
                process[i].join()
            a=count_pc-int(s3.group())
        pre=pc
        lock.acquire()
        return (a,pre,stack,top,rtop,tablecount,process_path)
    elif com[pc]==18:#merge
        pre=pc
        return (pc+1,pre,stack,top,rtop,tablecount,process_path)
    elif com[pc]==19:#func
        if args[2]=='f':
            #lstack[ltop.value]=(pre)
            #lstack[ltop.value+1]=0
            with open("label_stack.txt",'a') as f:
                f.write(str(count_pc-pre)+' '+str(process_number)+'.'+process_path+'\n')
            f.close()
            #ltop.value = ltop.value+2
            (c,top)=pop1(stack,top)
            push(pre+1,stack,top)
            push(c,stack,top)
        pre=pc
        #add_path(opr)
        process_path='f'+str(opr[pc])+'.'+process_path
        return (pc+1,pre,stack,top,rtop,tablecount,process_path)
    elif com[pc]==20:#return
        if args[2]=='f':
            (d,top) = pop1(stack,top)
            (c,top) = pop1(stack,top)
            push(d,stack,top)
        elif args[2]=='b':
            #ltop.value=ltop.value-1
            #pc=int(lstack[ltop.value])
            #pc=pc-2
            #ltop.value=ltop.value-1
            c=int(lstack[ltop.value])-1
            ltop.value=ltop.value-2
        #cut_path(opr)
        for i in range(0,len(process_path),1):
            if process_path[i] == '.':
                process_path=process_path[i+1:len(process_path)]
                break
        pre=pc
        return (c,pre,stack,top,rtop,tablecount,process_path)
    elif com[pc]==21:#w_label
        if args[2]=='f':
            #lstack[ltop.value]=(pre)
            #lstack[ltop.value+1]=0
            with open("label_stack.txt",'a') as f:
                f.write(str(count_pc-pre)+' '+str(process_number)+'.'+process_path+'\n')
            f.close()
            #ltop.value = ltop.value+2
        elif args[2]=='b':
            pc=int(lstack[ltop.value])-2
            ltop.value=ltop.value-2
        #add_path(opr)
        process_path='w'+str(opr[pc])+'.'+process_path
        pre=pc
        return (pc+1,pre,stack,top,rtop,tablecount,process_path)
    elif com[pc]==22:#w_end
        #cut_path(opr)
        if args[2]=='f':
            #lstack[ltop.value]=(pre)
            #lstack[ltop.value+1]=0
            with open("label_stack.txt",'a') as f:
                f.write(str(count_pc-pre)+' '+str(process_number)+'.'+process_path+'\n')
            f.close()
        elif args[2]=='b':
            pc=int(lstack[ltop.value])-2
            ltop.value=ltop.value-2
            #ltop.value = ltop.value+2
        process_path=process_path.replace('w'+str(opr[pc])+'.','')
        return (pc+1,pre,stack,top,rtop,tablecount,process_path)

def execution(command,opr,start,end,count_pc,stack,address,value,tablecount,rstack,lstack,rtop,ltop,endflag,variable_region,lock,process_number,process_path,process_count,terminate_flag,flag_number):
    pc=start
    pre=pc
    top=len(stack)
    num_variables = tablecount.value
    if args[2]=='f':
        while pc!=end or command[pre]==17:
            lock.acquire()
            #if parpath!=0:
            #   lock.acquire()
            if command[pc]==1:
                command1='   ipush'
            elif command[pc]==2:
                command1='    load'
            elif command[pc]==3:
                command1='   store'
            elif command[pc]==4:
                command1='     jpc'
            elif command[pc]==5:
                command1='     jmp'
            elif command[pc]==6:
                command1='      op'
            elif command[pc]==7:
                command1='   label'
            elif command[pc]==10:
                command1='     par'
            elif command[pc]==11:
                command1='   alloc'
            elif command[pc]==12:
                command1='    free'
            elif command[pc]==13:
                command1='    proc'
            elif command[pc]==14:
                command1='proc_end'
            elif command[pc]==15:
                command1='   block'
            elif command[pc]==16:
                command1='     end'
            elif command[pc]==17:
                command1='    fork'
            elif command[pc]==18:
                command1='   merge'
            elif command[pc]==19:
                command1='    func'
            elif command[pc]==20:
                command1='  return'
            elif command[pc]==21:
                command1=' w_label'
            elif command[pc]==22:
                command1='   w_end'
            elif command[pc]==0:
                command1='     nop'
            with open("output.txt",'a') as f:
                f.write("~~~~~~~~Process"+process_number+" execute~~~~~~~~\n")
                f.write("path : "+process_path+"\n")
                f.write("pc = "+str(pc+1)+"   command = "+command1+":"+(str)(command[pc])+"    operand = "+str(opr[pc])+"\n")
            print("~~~~~~~~Process"+process_number+" execute~~~~~~~~")
            print("path : "+process_path)
            print("pc = "+str(pc+1)+"   command = "+command1+":"+(str)(command[pc])+"    operand = "+str(opr[pc])+"")
            (pc,pre,stack,top,rtop,tablecount,process_path)=executedcommand(stack,rstack,lstack,command,opr,pc,pre,top,rtop,ltop,address,value,tablecount,variable_region,lock,process_number,process_path,count_pc,process_count,terminate_flag,flag_number)
            """
            print("~~~~~~~~Process"+process_number+" execute~~~~~~~~")
            print("path : "+process_path)
            print("pc = "+str(pre+1)+"   command = "+command1+":"+(str)(command[pre])+"    operand = "+str(opr[pre])+"")
            """
            if command[pre]==17:
                with open("output.txt",'a') as f:
                    f.write("---fork end--- (process "+process_number+")\n")
                print("---fork end--- (process "+process_number+")")
            with open("output.txt",'a') as f:
                f.write("executing stack:       "+str(stack[0:])+"\n")
                f.write("shared variable stack: "+str(value[0:tablecount.value])+"\n")
                f.write("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n")
            print("executing stack:       "+str(stack[0:])+"")
            print("shared variable stack: "+str(value[0:tablecount.value])+"")
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")
            if command[pre] == 12:
                with open("variable_region.txt",'w') as f:
                    for i in range(0,num_variables,1):
                        f.write(""+str(variable_region[i])+" ")
            #if not command[pre]==17:            
            lock.release()
        #if command[pre]==10 and opr[pre]==1:
        #print("process" +str(flag_number)+" terminate flag. executed command is "+str(command[pre])+" pc is"+ str(pc)+" end is "+str(end))
        terminate_flag[flag_number]=1
    if args[2]=='b':
        while pc!=end or command[pre]==17:
            lock.acquire()
            #if parpath!=0:
            #   lock.acquire()
            if command[pc]==1:
                command1='   ipush'
            elif command[pc]==2:
                command1='    load'
            elif command[pc]==3:
                command1='   store'
            elif command[pc]==4:
                command1='     jpc'
            elif command[pc]==5:
                command1='     jmp'
            elif command[pc]==6:
                command1='      op'
            elif command[pc]==7:
                command1='   label'
            elif command[pc]==8:
                command1='    rjmp'
            elif command[pc]==9:
                command1='  restore'
            elif command[pc]==10:
                command1='     par'
            elif command[pc]==11:
                command1='   alloc'
            elif command[pc]==12:
                command1='    free'
            elif command[pc]==13:
                command1='    proc'
            elif command[pc]==14:
                command1='     ret'
            elif command[pc]==15:
                command1='   block'
            elif command[pc]==16:
                command1='     end'
            elif command[pc]==17:
                command1='    fork'
            elif command[pc]==18:
                command1='   merge'
            elif command[pc]==19:
                command1='    func'
            elif command[pc]==20:
                command1='  return'
            elif command[pc]==21:
                command1=' w_label'
            elif command[pc]==22:
                command1='   w_end'
            elif command[pc]==0:
                command1='     nop'
            s=re.search(r'(\d+\.)+',lstack[ltop.value+1])
            s2=re.search(r'(\d+\.)+',rstack[rtop.value+1])
            #if flag_number==9:
            #    print(process_number)
            #    print(s2.group())
            #    print(str(rtop.value))
            #print("path: "+str(process_path)+"  num:"+str(process_number)+"  s:"+str(s.group()))
            if (process_number+"."==s2.group() and command[pc]==9) or (process_number+"."==s.group() and (command[pc]==8 or command[pc]==14 or command[pc]==21 or command[pc]==22)) or (command[pc]!=8 and command[pc]!=9 and command[pc]!=14 and command[pc]!=21 and command[pc]!=22):
                with open("reverse_output.txt",'a') as f:
                    f.write("~~~~~~~~Process"+process_number+" execute~~~~~~~~\n")
                    f.write("path : "+process_path+"\n")
                    f.write("pc = "+str(pc+1)+"("+str(count_pc-pc)+")   command = "+command1+":"+(str)(command[pc])+"    operand = "+str(opr[pc])+"\n")
                print("~~~~~~~~Process"+process_number+" execute~~~~~~~~")
                print("path : "+process_path)
                print("pc = "+str(pc+1)+"("+str(count_pc-pc)+")   command = "+command1+":"+(str)(command[pc])+"    operand = "+str(opr[pc])+"")
                (pc,pre,stack,top,rtop,tablecount,process_path)=executedcommand(stack,rstack,lstack,command,opr,pc,pre,top,rtop,ltop,address,value,tablecount,variable_region,lock,process_number,process_path,count_pc,process_count,terminate_flag,flag_number)
            #print("~~~~~~~~Process"+process_number+" execute~~~~~~~~")
            #print("path : "+process_path)
            #print("pc = "+str(pre+1)+"   command = "+command1+":"+(str)(command[pre])+"    operand = "+str(opr[pre])+"")
                #print("executing stack:       "+str(stack[0:])+"")
                if command[pre]==17:
                    with open("reverse_output.txt",'a') as f:
                        f.write("---fork end--- (process "+process_number+")\n")
                    print("---fork end--- (process "+process_number+")")
                with open("reverse_output.txt",'a') as f:
                    f.write("shared variable stack: "+str(value[0:tablecount.value])+"\n\n")
                print("shared variable stack: "+str(value[0:tablecount.value])+"\n")
            if command[pre] == 12:
                with open("variable_region.txt",'w') as f:
                    for i in range(0,num_variables,1):
                        f.write(""+str(variable_region[i])+" ")
            lock.release()
        #print("process" +str(flag_number)+" terminate flag. executed command is "+str(command[pre])+" pc is"+ str(pc)+" end is "+str(end))
        terminate_flag[flag_number]=1
            #if parpath!=0:
            #    if mode=='2':
            #        lock.acquire(False)
            #        mlock.release()
            #    elif mode=='1':
            #        lock.release()
        #endflag.value=1
    """
    #backward mode
    elif args[2]=='b':
        while pc<end:
            if parpath!=0:
                lock.acquire()
            if args[3]!='q':
                if command[pc]==0:
                    command1='    nop'
                elif command[pc]==7:
                    command1='  label'
                elif command[pc]==8:
                    command1='   rjmp'
                elif command[pc]==9:
                    command1='restore'
                elif command[pc]==10:
                    command1='    par'
                elif command[pc]==11:
                    command1='  alloc'
                elif command[pc]==12:
                    command1='   free'
                print("~~~~~~~~Process"+str(parpath)+" execute~~~~~~~~")
                print("pc = "+str(pc+1)+"   command = "+command1+"   operand = "+str(opr[pc])+"")
            (pc,pre,stack,top,rtop,tablecount)=executedcommand(stack,rstack,lstack,command[pc],opr[pc],pc,pre,top,rtop,ltop,address,value,parpath,tablecount,variable_region)
            if args[3]!='q':
                print("shared variable stack: "+str(value[0:tablecount.value])+"")
            if parpath!=0:
                lock.acquire(False)
                mlock.release()
        endflag.value=1
        with open("variable_region.txt",'w') as f:
            for i in range(0,len(variable_region),1):
                f.write(""+str(variable_region[i])+" ")
    
    """
    return stack        

def coderead():
    global codes
    global com
    global opr
    global count_pc
    global parflag
    f=open(args[1],mode='r')
    codes=f.read()
    f.close()
    for i in range(0,len(codes),9):
        t1=codes[i:i+2]
        s1=re.search(r'\d+',t1)
        t2=codes[i+2:i+8]
        s2=re.search(r'\d+',t2)
        com.append((int)(s1.group()))
        opr.append((int)(s2.group()))
        #if ((int)(s1.group())==10 and (int)(s2.group())==0):
        #    start.append(count_pc)
        #elif ((int)(s1.group())==10 and (int)(s2.group())==1):
        #    end.append(count_pc)
        #    parflag=parflag+1
        count_pc=count_pc+1
    #with open("variable_region.txt","r") as f:
    #    buf = f.read()
    #    variable_region = re.findall(r'[-]?\d+',buf)
    #return variable_region

def backward():
    global ldata
    global rdata
    global stack
    if args[2]=='b':
        path4='lstack.txt'
        path5='rstack.txt'
        path7='stack.txt'
        f4=open(path4,mode='r')
        f5=open(path5,mode='r')
        f7=open(path7,mode='r')
        temp=f4.read()
        ldata=re.findall(r'[-]?\d+',temp)
        temp=f5.read()
        rdata=re.findall(r'[-]?\d+',temp)
        temp=f7.read()
        stack=re.findall(r'[-]?\d+',temp)
        f4.close()
        f5.close()
        f7.close()

def forward(com,opr,count_pc):
    #if args[2]!='f' and args[2]!='b':
    #path2=args[2]
    f2=open("inv_code.txt",mode='w')
    for i in range(0,count_pc,1):
        if com[count_pc-i-1]==7:
            f2.write(" 8     0\n")
        elif com[count_pc-i-1]==3:
            f2.write(" 9 "+str(opr[count_pc-i-1]).rjust(5)+"\n")
        elif com[count_pc-i-1]==4:
            f2.write(" 7     0\n")
        elif com[count_pc-i-1]==5:
            f2.write(" 7     0\n")
        elif com[count_pc-i-1]==10:
            if opr[count_pc-i-1]==0:
                f2.write("10 "+str(1).rjust(5)+"\n")
            elif opr[count_pc-i-1]==1:
                f2.write("10 "+str(0).rjust(5)+"\n")
        elif com[count_pc-i-1]==11:
            f2.write("12 "+str(opr[count_pc-i-1]).rjust(5)+"\n")
        elif com[count_pc-i-1]==12:
            f2.write("11 "+str(opr[count_pc-i-1]).rjust(5)+"\n")
        elif com[count_pc-i-1]==13:
            pname="p"+str(opr[count_pc-i-1])
            f2.write("14 "+pname.rjust(5)+"\n")
        elif com[count_pc-i-1]==14:
            pname="p"+str(opr[count_pc-i-1])
            f2.write("13 "+pname.rjust(5)+"\n")
        elif com[count_pc-i-1]==15:
            if com[count_pc-i]==5 and com[count_pc-i+1]==7 and com[count_pc-i+2]==16:
                bname="c"+str(opr[count_pc-i-1])
            else:
                bname="b"+str(opr[count_pc-i-1])
            f2.write("16 "+bname.rjust(5)+"\n")
        elif com[count_pc-i-1]==16:
            if com[count_pc-i-2]==7 and com[count_pc-i-3]==5 and com[count_pc-i-4]==15:
                bname="c"+str(opr[count_pc-i-1])
            else:
                bname="b"+str(opr[count_pc-i-1])
            f2.write("15 "+bname.rjust(5)+"\n")
        elif com[count_pc-i-1]==17:
            aname="a"+str(opr[count_pc-i-1])
            f2.write("18 "+aname.rjust(5)+"\n")
        elif com[count_pc-i-1]==18:
            aname="a"+str(opr[count_pc-i-1])
            f2.write("17 "+aname.rjust(5)+"\n")
        elif com[count_pc-i-1]==19:
            fname="f"+str(opr[count_pc-i-1])
            f2.write("20 "+fname.rjust(5)+"\n")
        elif com[count_pc-i-1]==20:
            fname="f"+str(opr[count_pc-i-1])
            f2.write("19 "+fname.rjust(5)+"\n")
        elif com[count_pc-i-1]==21:
            wname="w"+str(opr[count_pc-i-1])
            f2.write("22 "+wname.rjust(5)+"\n")
        elif com[count_pc-i-1]==22:
            wname="w"+str(opr[count_pc-i-1])
            f2.write("21 "+wname.rjust(5)+"\n")
        else:
            f2.write(" 0     0\n")
    f2.close()
        #print("forward code is converted into inverting code.")
    """
    elif args[2]=='f':
        path='lstack.txt'
        f=open(path,'w')
        for i in range(0,ltop,2):
            f.write(""+str(count_pc-lstack[i])+" "+str(lstack[i+1])+" ")
        f.close()

        path3='rstack.txt'
        f3=open(path3,'w')
        for i in range(0,rtop,1):
            f3.write(""+str(rstack[i])+" ")
        f3.close()

        path6='stack.txt'
        f6=open(path6,'w')
        for i in range(0,len(value),1):
            f6.write(""+str(value[i])+" ")
        f6.close()
    """

if __name__ == '__main__':
    start_time = time.time()
    start=[]
    end=[]
    tabledata=[]
    tablecount= Value('i',0)
    address = Array('i',10)
    value = Array('i',100)
    rstack = Array('i',100000)
    lstack = Array('i',100000)
    rtop = Value('i',0)
    ltop = Value('i',0)
    endflag={}
    endflag0=Value('i',0)
    notlabelflag=0
    lock=Lock()
    variable_region = []
    process_number='0'
    process_path='E'
    process_count = Value('i',0)
    terminate_flag = Array('i',100)
    for i in range(0,100,1):
        terminate_flag[i]=0
    
    mlock = Lock()
    lockfree  = Lock()
    a='1'
    #if os.path.getsize("variable_region.txt") <=0:
    #    with open("variable_region.txt",'w') as f:
    #        f.write("0 0 0")
    path='table.txt'
    f=open(path,mode='r')
    tabledata=f.read()
    f.close()
    if args[2]=='f':
        with open("variable_table.txt",'w') as f:
            f.write("")
        f.close()
        with open("value_stack.txt",'w') as f:
            f.write("")
        f.close()
        with open("label_stack.txt",'w') as f:
            f.write("")
        f.close()
        with open("output.txt",'w') as f:
            f.write("")
        f.close()
    elif args[2]=='b':
        with open("label_stack.txt",'r') as f:
            label_stack=f.read().split()
        ltop.value=len(label_stack)-2
        with open("value_stack.txt",'r') as f:
            value_stack=f.read().split()
        rtop.value=len(value_stack)-2
        with open("reverse_output.txt",'w') as f:
            f.write("")
        f.close()
    k=0

    #backward()
    """
    if len(sys.argv)<4:
        #print("convert into inv_code.txt")
        coderead(start,end,variable_region)
        forward(ltop.value,rtop.value)
        sys.exit()
    """
    coderead()
    #for i in range(0,count_pc,1):
    #    print(com[i],opr[i])
    if args[2]=='f':
        execution(com,opr,0,count_pc,count_pc,stack,address,value,tablecount,rstack,lstack,rtop,ltop,endflag0,variable_region,lock,process_number,process_path,process_count,terminate_flag,0)
    elif args[2]=='c':
        forward(com,opr,count_pc)
    elif args[2]=='b':
        execution(com,opr,0,count_pc,count_pc,stack,address,value,tablecount,value_stack,label_stack,rtop,ltop,endflag0,variable_region,lock,process_number,process_path,process_count,terminate_flag,0)
    """
    #forward mode
    if args[2]=='f':
        (start,end,variable_region)=coderead(start,end,variable_region)
        for i in range(0,parflag,1):
            endflag[i] = Value('i',0)
            lock[i] = Lock()
        if parflag!=0:
            if args[3]=='q':
                mode='1'
            else:
                mode=input('mode   1:auto 2:select >> ')
            stack=execution(mode,lockfree,lockfree,com,opr,0,start[0],stack,address,value,tablecount,rstack,lstack,rtop,ltop,endflag0,0,variable_region)
            if mode=='2':
                for i in range(0,parflag,1):
                    lock[i].acquire()
                process={}
                for i in range(0,parflag,1):        
                    process[i]=Process(target=execution,args=(mode,lock[i],mlock,com,opr,start[i],end[i],stack,address,value,tablecount,rstack,lstack,rtop,ltop,endflag[i],i+1,variable_region))
            if mode=='1':
                process={}
                for i in range(0,parflag,1):        
                    process[i]=Process(target=execution,args=(mode,lock[0],mlock,com,opr,start[i],end[i],stack,address,value,tablecount,rstack,lstack,rtop,ltop,endflag[i],i+1,variable_region))
            for i in range(0,parflag,1):
                    process[i].start()
            if mode=='2':
                while a!='esc':
                    a=input('>> ')
                    mlock.acquire(False)
                    ifflag=0
                    for i in range(0,parflag,1):
                        if a==str(i+1) and endflag[i].value!=1 and ifflag==0:
                            ifflag=1
                            lock[i].release()
            for i in range(0,parflag,1):
                process[i].join()
            for i in range(0,tablecount.value,1):
                stack[i]=value[i]
            execution(mode,lockfree,lockfree,com,opr,end[parflag-1]+1,len(com),stack,address,value,tablecount,rstack,lstack,rtop,ltop,endflag0,0,variable_region)
        elif parflag==0:
            mode='1'
            execution(mode,lockfree,mlock,com,opr,0,len(com),stack,address,value,tablecount,rstack,lstack,rtop,ltop,endflag0,0,variable_region)
        forward(ltop.value,rtop.value)
        """
    """
    elif args[2]=='b':
        (start,end,variable_region)=coderead(start,end,variable_region)
        for i in range(0,parflag,1):
            endflag[i] = Value('i',0)
            lock[i] = Lock()
        for i in range(0,len(ldata),1):
            lstack[i]=int(ldata[i])
            ltop.value=ltop.value+1
        for i in range(0,len(rdata),1):
            rstack[i]=int(rdata[i])
            rtop.value=rtop.value+1
        #for i in range(0,len(stack),1):
            #value[i]=int(stack[i])
        ltop.value=ltop.value-1
        rtop.value=rtop.value-1
        mode='0'
        if parflag!=0:
            #______measure time mode_________ 
            if args[3]=='q':
                mode='1'
            else:
                mode=input('mode   1:auto  2:select >> ')
            for i in range(0,parflag,1):
                lock[i].acquire()
            process={}
            execution(mode,lockfree,lockfree,com,opr,0,end[0],stack,address,value,tablecount,rstack,lstack,rtop,ltop,endflag0,0,variable_region)
            for i in range(0,parflag,1):
                process[i]=Process(target=execution,args=(mode,lock[parflag-i-1],mlock,com,opr,end[i],start[i],stack,address,value,tablecount,rstack,lstack,rtop,ltop,endflag[i],parflag-i,variable_region))
            for i in range(0,parflag,1):
                process[i].start()
            a='2'
            if len(ldata)==0:
                notlabelflag = 1
            if mode=='2':
                if notlabelflag==0:
                    while a!='esc':
                        a=input('process '+str(lstack[ltop.value])+' ')
                        mlock.acquire(False)
                        for i in range(0,parflag,1):
                            if int(lstack[ltop.value])==i+1:
                                lock[i].release()
                elif notlabelflag==1:
                    preprocess=0
                    while a!='esc':
                        endcount=0
                        a=input('process '+str(lstack[ltop.value])+' ')
                        mlock.acquire(False)
                        if int(rstack[rtop.value])!=0:
                            for i in range(0,parflag,1):
                                if int(rstack[rtop.value])==i+1:
                                    preprocess=i
                                    lock[i].release()
                        elif int(rstack[rtop.value])==0 and ((preprocess==0 and endflag[1].value==0) or (preprocess==1 and endflag[0].value==0)):
                            lock[preprocess].release()
                        elif (preprocess==0 and endflag[1].value==1) or (preprocess==1 and endflag[0].value==1):
                            if preprocess==0:
                                lock[1].release()
                            elif preprocess==1:
                                lock[0].release()
                                #for i in range(0,parflag,1):
                                #    if preprocess==i and endflag[parflag-i-1].value==0:
                                #        lock[preprocess].release()
                                #for i in range(0,parflag,1):
                                #    if preprocess==i and endflag[parflag-i-1].value==1:
                                #        lock[parflag-i-1].release()
                        for i in range(0,parflag,1):
                            if endflag[i].value==1:
                                endcount=endcount+1
                        if endcount==parflag:
                            a='esc'

            elif mode=='1':
                if notlabelflag==0:
                    while a!='esc':
                        mlock.acquire()
                        ifflag=0
                        endcount=0
                        for i in range(0,parflag,1):
                            if (int(lstack[ltop.value])==i+1 and ifflag==0):
                                lock[i].release()
                                ifflag=1
                        for i in range(0,parflag,1):
                            if endflag[i].value==1:
                                endcount=endcount+1
                        if endcount==parflag:
                            a='esc'
                elif notlabelflag==1:
                    preprocess=0
                    while a!='esc':
                        mlock.acquire()
                        ifflag=0
                        endcount=0
                        if int(rstack[rtop.value]!=0):
                            for i in range(0,parflag,1):
                                if (int(rstack[rtop.value])==i+1 and ifflag==0):
                                    preprocess=i
                                    lock[i].release()
                                    ifflag=1
                        elif int(rstack[rtop.value])==0 and ((preprocess==0 and endflag[1].value==0) or (preprocess==1 and endflag[0].value==0)):
                            lock[preprocess].release()
                        elif (preprocess==0 and endflag[1].value==1) or (preprocess==1 and endflag[0].value==1):
                            if preprocess==0:
                                lock[1].release()
                            elif preprocess==1:
                                lock[0].release()
                            #for i in range(0,parflag,1):
                            #    if preprocess==i and endflag[parflag-i-1].value==0:
                            #        lock[preprocess].release()
                            #for i in range(0,parflag,1):
                            #    if preprocess==i and endflag[parflag-i-1].value:
                            #        lock[parflag-i-1].release()
                        for i in range(0,parflag,1):
                            if endflag[i].value==1:
                                endcount=endcount+1
                        if endcount==parflag:
                            a='esc'
            for i in range(0,parflag,1):
                process[i].join()
            execution(mode,lockfree,lockfree,com,opr,start[parflag-1]+1,count_pc,stack,address,value,tablecount,rstack,lstack,rtop,ltop,endflag0,0,variable_region)
        elif parflag==0:
            execution(mode,lockfree,lockfree,com,opr,0,len(com),stack,address,value,tablecount,rstack,lstack,rtop,ltop,endflag0,0,variable_region)
    """
    """
    elif args[2]=='c':
        (start,end,variable_region)=coderead(start,end,variable_region)
        forward(ltop.value,rtop.value)
    """
    elapsed_time = time.time()-start_time
    print("elapsed_time:{0}".format(elapsed_time) + "[sec]")