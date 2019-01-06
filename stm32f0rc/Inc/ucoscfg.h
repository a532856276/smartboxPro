/*
*********************************************************************************************************
*                                              EXAMPLE CODE
*
*                          (c) Copyright 2003-2006; Micrium, Inc.; Weston, FL
*
*               All rights reserved.  Protected by international copyright laws.
*               Knowledge of the source code may NOT be used to develop a similar product.
*               Please help us continue to provide the Embedded community with the finest
*               software available.  Your honesty is greatly appreciated.
*********************************************************************************************************
*/

/*
*********************************************************************************************************
*
*                                      APPLICATION CONFIGURATION
*
*                                     ST Microelectronics STM32
*                                              with the
*                                   STM3210B-EVAL Evaluation Board
*
* Filename      : app_cfg.h
* Version       : V1.10
* Programmer(s) : BAN
*********************************************************************************************************
*/

#ifndef  __UCOSCFG_H__
#define  __UCOSCFG_H__

/*
*********************************************************************************************************
*                                       MODULE ENABLE / DISABLE
*********************************************************************************************************
*/

//#define  APP_OS_PROBE_EN                         DEF_ENABLED
//#define  APP_PROBE_COM_EN                        DEF_ENABLED

/*
*********************************************************************************************************
*                                              TASKS NAMES
*********************************************************************************************************
*/


/*
*********************************************************************************************************
*                                            TASK PRIORITIES
*********************************************************************************************************
*/
#define  APP_TASK_LED1_PRIO                               3
#define  APP_TASK_LED2_PRIO                               4

/*
*********************************************************************************************************
*                                            TASK STACK SIZES
*                             Size of the task stacks (# of OS_STK entries)
*********************************************************************************************************
*/
#define  APP_TASK_LED1_STK_SIZE                         128
#define  APP_TASK_LED2_STK_SIZE                         128

/*
*********************************************************************************************************
*                                                  LIB
*********************************************************************************************************
*/

#define  uC_CFG_OPTIMIZE_ASM_EN                 DEF_ENABLED
#define  LIB_STR_CFG_FP_EN                      DEF_DISABLED

/*
*********************************************************************************************************
*                                                 PROBE
*********************************************************************************************************
*/

//#define  OS_PROBE_TASK                                     0    /* Task will be created for uC/Probe OS Plug-In.        */
//#define  OS_PROBE_TMR_32_BITS                              0    /* uC/Probe OS Plugin timer is a 16-bit timer.          */
//#define  OS_PROBE_TIMER_SEL                                2    /* Select timer 2.                                      */
//#define  OS_PROBE_HOOKS_EN                                 1    /* Hooks to update OS_TCB profiling members included.   */
//#define  OS_PROBE_USE_FP                                   1




#endif
