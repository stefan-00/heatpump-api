# WEB-RC Full Tree (access level 4444)


## WEB-RC root  _(bn=1, lv=0)_

|  |
|---|
| main menu |
| global |
| MCR-BMS |
| interfaces |
| configuration |
| diagrams |
| system survey |


### global  _(bn=1, lv=1)_

|  |
|---|
| global |
| service |
| structure |


#### service  _(bn=1, lv=2)_

|  |
|---|
| global service |
| software |
| cold- warm start |
| access codes |


##### software  _(bn=1, lv=3)_

|  |  |
|---|---|
| service software |  |
| Language English |  |


##### cold- warm start  _(bn=2, lv=3)_

|  |  |
|---|---|
| service c-w-start |  |
| warm start 0 |  |
| coldStSys 0 |  |


##### access codes  _(bn=3, lv=3)_

|  |  |
|---|---|
| service author. |  |
| level 1 9999 |  |
| level 2 1111 |  |
| level 3 4444 |  |
| protect 2 |  |
| service24 0 |  |
| timer 00:00 |  |


#### structure  _(bn=2, lv=2)_

|  |
|---|
| global structure |
| WEB |


##### WEB  _(bn=1, lv=3)_

|  |  |
|---|---|
| structure Web |  |
| contr.name HPM-800B7F |  |
| protect 1 |  |
| username 1 user |  |
| level 1 11111111 |  |
| username 2 operator |  |
| level 2 22222222 |  |
| username 3 service |  |
| level 3 44444444 |  |


### MCR-BMS  _(bn=2, lv=1)_

|  |
|---|
| MCR-BMS |
| timers |
| heat source |
| buffer tank |
| domHotWater |
| heatCirc. |
| trend |
| photovoltaics |
| Smart Grid |
| Extended configur. |


#### timers  _(bn=1, lv=2)_

|  |
|---|
| MCR-BMS timers |
| timer curVal |
| timer chan. select. |
| timer status |
| timer service |


##### timer curVal  _(bn=1, lv=3)_

|  |  |
|---|---|
| timer curVal |  |
| season: summer |  |
| day: friday |  |


##### timer chan. select.  _(bn=2, lv=3)_

|  |
|---|
| timer chanSele |
| domHotWat. |
| heatc.1 |
| heatc.2 |
| quiet |


###### domHotWat.  _(bn=1, lv=4)_

|  |
|---|
| timer timer DHW |
| week program |
| special-non-occup. |
| special-occup. |
| priority |


###### week program  _(bn=1, lv=5)_

|  |  |
|---|---|
| tmr DHW weeklyPrg |  |
| group 3 |  |
| mo numOT 2 |  |
| mo beg OT1 11:00 |  |
| mo end OT1 14:00 |  |
| mo beg OT2 14:00 |  |
| mo end OT2 11:00 |  |


###### special-non-occup.  _(bn=2, lv=5)_

|  |  |
|---|---|
| tmr DHW SNO-time |  |
| numSNO 1 |  |
| begSNO1 22.02.25 |  |
| endSNO1 28.02.25 |  |


###### special-occup.  _(bn=3, lv=5)_

|  |  |
|---|---|
| tmr DHW SO-time |  |
| numSOT 0 |  |


###### priority  _(bn=4, lv=5)_

|  |  |
|---|---|
| tmr DHW priority |  |
| typPrior 0 |  |


###### heatc.1  _(bn=2, lv=4)_

|  |
|---|
| timer timer hCu1 |
| week program |
| special-non-occup. |
| special-occup. |
| priority |


###### week program  _(bn=1, lv=5)_

|  |  |
|---|---|
| timer HC1 weeklyPrg |  |
| group 3 |  |
| mo numOT 2 |  |
| mo beg OT1 21:00 |  |
| mo end OT1 06:00 |  |
| mo beg OT2 06:00 |  |
| mo end OT2 21:00 |  |


###### special-non-occup.  _(bn=2, lv=5)_

|  |  |
|---|---|
| timer HC1 SNO-time |  |
| numSNO 0 |  |


###### special-occup.  _(bn=3, lv=5)_

|  |  |
|---|---|
| timer HC1 SO-time |  |
| numSOT 0 |  |


###### priority  _(bn=4, lv=5)_

|  |  |
|---|---|
| timer HC1 priority |  |
| typPrior 0 |  |


###### heatc.2  _(bn=3, lv=4)_

|  |
|---|
| timer timer hCu2 |
| week program |
| special-non-occup. |
| special-occup. |
| priority |


###### week program  _(bn=1, lv=5)_

|  |  |
|---|---|
| timer HC2 weeklyPrg |  |
| group 3 |  |
| mo numOT 2 |  |
| mo beg OT1 07:30 |  |
| mo end OT1 17:00 |  |
| mo beg OT2 17:00 |  |
| mo end OT2 07:30 |  |


###### special-non-occup.  _(bn=2, lv=5)_

|  |  |
|---|---|
| timer HC2 SNO-time |  |
| numSNO 1 |  |
| begSNO1 30.08.25 |  |
| endSNO1 20.05.26 |  |


###### special-occup.  _(bn=3, lv=5)_

|  |  |
|---|---|
| timer HC2 SO-time |  |
| numSOT 1 |  |
| begSOT1 --.--.-- |  |
| endSOT1 --.--.-- |  |
| SOT1numOT 0 |  |


###### priority  _(bn=4, lv=5)_

|  |  |
|---|---|
| timer HC2 priority |  |
| typPrior 0 |  |


###### quiet  _(bn=4, lv=4)_

|  |
|---|
| timer timer quiet |
| week program |
| special-non-occup. |
| special-occup. |
| priority |


###### week program  _(bn=1, lv=5)_

|  |  |
|---|---|
| timer QU weeklyPrg |  |
| group 0 |  |
| mo numOT 2 |  |
| mo beg OT1 00:00 |  |
| mo end OT1 24:00 |  |
| mo beg OT2 --:-- |  |
| mo end OT2 --:-- |  |
| tu numOT 2 |  |
| tu beg OT1 00:00 |  |
| tu end OT1 24:00 |  |
| tu beg OT2 --:-- |  |
| tu end OT2 --:-- |  |
| we numOT 2 |  |
| we beg OT1 00:00 |  |
| we end OT1 24:00 |  |
| we beg OT2 --:-- |  |
| we end OT2 --:-- |  |
| th numOT 2 |  |
| th beg OT1 00:00 |  |
| th end OT1 24:00 |  |
| th beg OT2 --:-- |  |
| th end OT2 --:-- |  |
| fr numOT 2 |  |
| fr beg OT1 00:00 |  |
| fr end OT1 24:00 |  |
| fr beg OT2 --:-- |  |
| fr end OT2 --:-- |  |
| sa numOT 2 |  |
| sa beg OT1 00:00 |  |
| sa end OT1 24:00 |  |
| sa beg OT2 --:-- |  |
| sa end OT2 --:-- |  |
| su numOT 2 |  |
| su beg OT1 00:00 |  |
| su end OT1 24:00 |  |
| su beg OT2 --:-- |  |
| su end OT2 --:-- |  |


###### special-non-occup.  _(bn=2, lv=5)_

|  |  |
|---|---|
| timer QU SNO-time |  |
| numSNO 0 |  |


###### special-occup.  _(bn=3, lv=5)_

|  |  |
|---|---|
| timer QU SO-time |  |
| numSOT 0 |  |


###### priority  _(bn=4, lv=5)_

|  |  |
|---|---|
| timer QU priority |  |
| typPrior 0 |  |


##### timer status  _(bn=3, lv=3)_

|  |
|---|
| timer status |
| domHotWat. |
| heatc.1 |
| heatc.2 |
| quiet |


###### domHotWat.  _(bn=1, lv=4)_

|  |  |
|---|---|
| timer stat. DHW |  |
| timer status timerProgram |  |
| curStat OT2 |  |
| nxtStat OT1 |  |
| timeDiff 834 min |  |


###### heatc.1  _(bn=2, lv=4)_

|  |  |
|---|---|
| timer stat. hCu1 |  |
| timer status timerProgram |  |
| curStat OT1 |  |
| nxtStat OT2 |  |
| timeDiff 534 min |  |


###### heatc.2  _(bn=3, lv=4)_

|  |  |
|---|---|
| timer stat. hCu2 |  |
| timer status timerProgram |  |
| curStat OT2 |  |
| nxtStat OT1 |  |
| timeDiff 624 min |  |


###### quiet  _(bn=4, lv=4)_

|  |  |
|---|---|
| timer stat. quiet |  |
| timer status timerProgram |  |
| curStat OT1 |  |
| nxtStat OT1 |  |
| timeDiff 11111 min |  |


##### timer service  _(bn=4, lv=3)_

|  |
|---|
| timer service |
| time |
| date |


###### time  _(bn=1, lv=4)_

|  |  |
|---|---|
| timer S-time |  |
| curTime 21:05 |  |


###### date  _(bn=2, lv=4)_

|  |  |
|---|---|
| timer S-date |  |
| curDate 22.05.26 |  |


#### heat source  _(bn=2, lv=2)_

|  |
|---|
| MCR-BMS HS |
| heat pump 1 |


##### heat pump 1  _(bn=1, lv=3)_

|  |
|---|
| HS heatp.1 |
| curValue |
| setpoints |
| function |
| status |
| manual oper. |
| service |


###### curValue  _(bn=1, lv=4)_

|  |  |
|---|---|
| heatp.1 curValue |  |
| outdoor 18.0 °C |  |
| system auto |  |
| oModLoc auto |  |
| mainten. off |  |
| HPOutdoor 18 °C |  |
| HPOutletTemp 25 °C |  |
| HPInletTemp 24 °C |  |
| HPTankTemp 49 °C |  |


###### setpoints  _(bn=2, lv=4)_

|  |  |
|---|---|
| heatp.1 setpoints |  |
| setpointHC 2 °C |  |
| setp.DHW 2 °C |  |


###### function  _(bn=3, lv=4)_

|  |
|---|
| heatp.1 funct. |
| setpoint limitation |
| boost |
| controller |
| Bivalence |
| Aquarea |
| busStatus |
| pu/va exercise |


###### setpoint limitation  _(bn=1, lv=5)_

|  |  |
|---|---|
| heatp.1 F-SP.limit |  |
| maxSP 70.0 °C |  |


###### boost  _(bn=2, lv=5)_

|  |  |
|---|---|
| heatp.1 F-boost. |  |
| active 1 |  |
| boost DHW1 0 % |  |
| boost.hCu 0.0 °C |  |


###### controller  _(bn=3, lv=5)_

|  |  |
|---|---|
| heatp.1 F-controller |  |
| longDes heat pump 1 |  |


###### Bivalence  _(bn=4, lv=5)_

|  |  |
|---|---|
| heatp.1 F-Bival. |  |
| type 1 |  |
| limit 0.0 °C |  |


###### Aquarea  _(bn=5, lv=5)_

|  |
|---|
| heatp.1 F-Aquarea |
| settings |
| service |
| Modus |


###### settings  _(bn=1, lv=6)_

|  |  |
|---|---|
| heatp.1 F-set |  |
| Thermost 0 |  |
| Tank 1 |  |
| BoosterH 1 |  |
| AntiFr 1 |  |
| BoostDel 60 min |  |
| HeaterC 9 |  |
| OutTOn -10 °C |  |
| BasePHeat 0 |  |


###### service  _(bn=2, lv=6)_

|  |  |
|---|---|
| heatp.1 F-service |  |
| Deice 0 |  |
| SPumpDW 0 |  |
| SPump 0 |  |
| Reset1 0 |  |
| Reset2 0 |  |
| Errorhist H76 |  |
| DeiceAuto 0 |  |
| DeiceULiOT 7.0 °C |  |
| DeiceLLiOT -2.0 °C |  |
| DeiceRunt 30 min |  |
| DeiceCurT 0 min |  |


###### Modus  _(bn=3, lv=6)_

|  |  |
|---|---|
| heatp.1 F-Modus |  |
| Quiet 0 |  |
| Heater 1 |  |
| OptTank 0 |  |


###### busStatus  _(bn=6, lv=5)_

|  |  |
|---|---|
| heatp.1 F-BusStat |  |
| statDelay 180 min |  |


###### pu/va exercise  _(bn=7, lv=5)_

|  |  |
|---|---|
| heatp.1 F-pu/va exer |  |
| duration 120 s |  |


###### status  _(bn=4, lv=4)_

|  |  |
|---|---|
| heatp.1 status |  |
| opStatus Blocked / off |  |
| trouble normal |  |
| source no demand |  |
| busStat no error |  |
| troubInd normal |  |
| opStatCode 00 |  |
| trbStatCode 00 |  |
| OP-OFF/ON off |  |
| OP-HEAT on |  |
| OP-TANK off |  |
| OP-FORCE off |  |
| Stat-Heater off |  |
| Stat-Booster off |  |
| Stat-Warning off |  |
| Stat-Defrost off |  |
| Errorcode --- |  |
| Freq 0 |  |
| ServiceOP off |  |
| StatEHeat 9 kW |  |
| auto off |  |
| Quiet off |  |
| ExtSwOff off |  |


###### manual oper.  _(bn=5, lv=4)_

|  |  |
|---|---|
| heatp.1 manOper |  |
| no parameter |  |


###### service  _(bn=6, lv=4)_

|  |
|---|
| heatp.1 service |
| generalVal |
| sensor correction |
| terminal ass. |


###### generalVal  _(bn=1, lv=5)_

|  |  |
|---|---|
| heatp.1 S-gen.Val |  |
| numStartHP 75490 |  |
| heatpump 46389 h |  |
| E-heat 0 h |  |
| DHW-E-heat 0 h |  |


###### sensor correction  _(bn=2, lv=5)_

|  |  |
|---|---|
| heatp.1 S-senCor |  |
| outdoor 0.0 K |  |


###### terminal ass.  _(bn=3, lv=5)_

|  |  |
|---|---|
| heatp.1 s-termAss |  |
| outdoor 41 |  |
| system 152 |  |
| oModLoc 151 |  |
| mainten. 141 |  |
| htAmount 0 |  |
| amtEner 0 |  |
| HP-rel 0 |  |
| HP-biv 0 |  |
| troubInd 13 |  |
| HP-heat 0 |  |
| HP-cooling 0 |  |


#### buffer tank  _(bn=3, lv=2)_

|  |
|---|
| MCR-BMS Buffer |
| curValue |
| setpoints |
| function |
| status |
| manual oper. |
| service |


##### curValue  _(bn=1, lv=3)_

|  |  |
|---|---|
| buffer curValue |  |
| buffer1 34.3 |  |
| oModLoc auto |  |


##### setpoints  _(bn=2, lv=3)_

|  |  |
|---|---|
| buffer setpoints |  |
| SP-zone1 20.0 °C |  |
| boostZ1 0.0 |  |


##### function  _(bn=3, lv=3)_

|  |
|---|
| buffer funct. |
| boost |
| ext. demand |
| signal |
| buffer tank |


###### boost  _(bn=1, lv=4)_

|  |  |
|---|---|
| buffer F-boost. |  |
| active 0 |  |
| boost HC1 10 % |  |
| boost HC2 10 % |  |


###### ext. demand  _(bn=2, lv=4)_

|  |  |
|---|---|
| buffer F-extDem |  |
| no parameter |  |


###### signal  _(bn=3, lv=4)_

|  |  |
|---|---|
| buffer F-signal |  |
| active 0 |  |
| TI-all 1 |  |
| uLimAddHS 130.0 °C |  |
| uLim-sol 130.0 °C |  |


###### buffer tank  _(bn=4, lv=4)_

|  |  |
|---|---|
| buffer F-buffer |  |
| maxTDHWta 70.0 °C |  |
| longDes buffer tank |  |
| minSwOf 5 min |  |


##### status  _(bn=4, lv=3)_

|  |  |
|---|---|
| buffer status |  |
| opStatus nom. oper. |  |
| trouble normal |  |
| source dem. HC1 |  |
| opStatCode 001 |  |
| trbStatCode 0 |  |


##### manual oper.  _(bn=5, lv=3)_

|  |  |
|---|---|
| buffer manOper |  |
| no parameter |  |


##### service  _(bn=6, lv=3)_

|  |
|---|
| buffer service |
| sensor correction |
| terminal ass. |


###### sensor correction  _(bn=1, lv=4)_

|  |  |
|---|---|
| buffer S-senCor |  |
| buffer1 0.0 K |  |


###### terminal ass.  _(bn=2, lv=4)_

|  |  |
|---|---|
| buffer S-termAss |  |
| demCFlHeat 0 |  |
| demConHeat 0 |  |
| buffer1 22 |  |
| buffer2 0 |  |
| buffer3 0 |  |
| solColl 0 |  |
| solRet 0 |  |
| addHS-Fl 0 |  |
| addHS-Ret 0 |  |
| earthB 0 |  |
| oModLoc 151 |  |
| Fl-T-He 0 |  |
| addHS 0 |  |
| solPu 0 |  |
| loadPu 0 |  |
| earthBPu 0 |  |
| zone2 0 |  |


#### domHotWater  _(bn=4, lv=2)_

|  |
|---|
| MCR-BMS DHW |
| curValue |
| setpoints |
| function |
| status |
| manual oper. |
| service |


##### curValue  _(bn=1, lv=3)_

|  |  |
|---|---|
| domHotWat curValue |  |
| DHWtank 49.0 °C |  |
| key off |  |
| oModLoc auto |  |


##### setpoints  _(bn=2, lv=3)_

|  |  |
|---|---|
| domHotWat setpoints |  |
| SP-OT1 52.0 °C |  |
| SP-OT2 45.0 °C |  |
| SP-OT3 45.0 °C |  |
| SP-OT4 45.0 °C |  |
| SP-NO 2.0 °C |  |
| SP-SNOT 2.0 °C |  |
| SP-DHWta 45.0 °C |  |


##### function  _(bn=3, lv=3)_

|  |
|---|
| domHotWat funct. |
| setpoint limitation |
| controller |
| therm. disinfection |


###### setpoint limitation  _(bn=1, lv=4)_

|  |  |
|---|---|
| domHotWat F-SP.limit |  |
| maxSP 70.0 °C |  |
| maxDemFl-T 70.0 °C |  |


###### controller  _(bn=2, lv=4)_

|  |  |
|---|---|
| F-controller |  |
| sys-type 2 |  |
| solar 0 |  |
| longDes domHotWater |  |


###### therm. disinfection  _(bn=3, lv=4)_

|  |  |
|---|---|
| domHotWat F-thermDes |  |
| active 0 |  |
| SP-DHWta 60.0 °C |  |
| SP-loadFl 85.0 °C |  |
| day 7 |  |
| time 01:00 |  |
| duration 5 min |  |
| maxDuration 300 min |  |


##### status  _(bn=4, lv=3)_

|  |  |
|---|---|
| domHotWat status |  |
| opStatus nom. oper. OT2 |  |
| trouble normal |  |
| source timer-OT2 ----- |  |
| troubInd normal |  |
| opStatCode 0040002 |  |
| trbStatCode 00 |  |


##### manual oper.  _(bn=5, lv=3)_

|  |  |
|---|---|
| domHotWat manOper |  |
| no parameter |  |


##### service  _(bn=6, lv=3)_

|  |
|---|
| domHotWat service |
| therm. disinfection |
| sensor correction |
| terminal ass. |


###### therm. disinfection  _(bn=1, lv=4)_

|  |  |
|---|---|
| domHotWat S-thermD |  |
| curDHWta 60.0 °C |  |
| time 03:40 |  |
| date 27.07.25 |  |
| intTmr 0.0 min |  |
| Reset-mess 0 |  |
| intTmr 0 min |  |


###### sensor correction  _(bn=2, lv=4)_

|  |  |
|---|---|
| domHotWat S-senCor |  |
| DHWtank 0.0 K |  |


###### terminal ass.  _(bn=3, lv=4)_

|  |  |
|---|---|
| domHotWat s-termAss |  |
| DHWtank 44 |  |
| DHWtank2 0 |  |
| release 0 |  |
| outdoor 0 |  |
| volFlow 0 |  |
| heatCapa 0 |  |
| htAmount 0 |  |
| system 0 |  |
| key 144 |  |
| oModRC 0 |  |
| oModLoc 151 |  |
| va-open 0 |  |
| va-close 0 |  |
| loadPu 0 |  |
| circPu 0 |  |
| thermDOn 0 |  |
| thermDSto 0 |  |
| troubInd 13 |  |
| VDV 0 |  |


#### heatCirc.  _(bn=5, lv=2)_

|  |
|---|
| MCR-BMS heat.circ |
| heatC. 1 |
| heatC. 2 |


##### heatC. 1  _(bn=1, lv=3)_

|  |
|---|
| heatC. heatC.1 |
| curValue |
| setpoints |
| function |
| status |
| manual oper. |
| service |


###### curValue  _(bn=1, lv=4)_

|  |  |
|---|---|
| heatCirc1 curValue |  |
| outdoor 18.0 °C |  |
| flow 21.3 °C |  |
| delOutT 20.5 °C |  |
| key off |  |
| oModLoc auto |  |


###### setpoints  _(bn=2, lv=4)_

|  |  |
|---|---|
| heatCirc1 setpoints |  |
| roomOT1 20.0 °C |  |
| roomOT2 20.0 °C |  |
| roomOT3 20.0 °C |  |
| roomOT4 20.0 °C |  |
| roomNO 20.0 °C |  |
| roomSNOT 14.0 °C |  |
| hCu-slope 0.5 |  |
| hCu-exp 1.10 |  |
| SP-Flow 20.0 °C |  |


###### function  _(bn=3, lv=4)_

|  |
|---|
| heatCirc1 funct. |
| summer shutdown |
| setpoint limitation |
| controller |
| screed drying |


###### summer shutdown  _(bn=1, lv=5)_

|  |  |
|---|---|
| heatCirc1 F-summersd |  |
| active 0 |  |
| type 1 |  |
| swOfTempOT 18.0 °C |  |
| swOfTempNO 13.0 °C |  |
| swOnTempOT 15.0 °C |  |
| swOnTempNO 11.0 °C |  |


###### setpoint limitation  _(bn=2, lv=5)_

|  |  |
|---|---|
| heatCirc1 F-SP.limit |  |
| active 1 |  |
| minFl 2.0 °C |  |
| maxFl 65.0 °C |  |
| posLim 1400.0 K/h |  |
| negLim 1400.0 K/h |  |
| maxDemFl-T 65.0 °C |  |


###### controller  _(bn=3, lv=5)_

|  |  |
|---|---|
| F-controller |  |
| contrOutp 3 |  |
| longDes heatC. 1 |  |


###### screed drying  _(bn=4, lv=5)_

|  |  |
|---|---|
| heatCirc1 F-screed |  |
| active 0 |  |
| initTemp 25.0 |  |
| dwellInitTemp 1 d |  |
| rateTmp+ 5.0 K |  |
| dwell+ 1 d |  |
| maxTemp 45.0 °C |  |
| dwellMaxTemp 3 d |  |
| rateTmp- 5.0 K |  |
| dwell- 1 d |  |
| optionPwFail 0 |  |
| max-Xw 50.0 K |  |
| dur-Xw 0.5 h |  |


###### status  _(bn=4, lv=4)_

|  |  |
|---|---|
| heatCirc1 status |  |
| opStatus nom. oper. OT1 |  |
| trouble normal |  |
| source timer-OT1 ---------- |  |
| contrOpen off |  |
| contrClos on |  |
| pump on |  |
| troubInd normal |  |
| opStatCode 00000 |  |
| trbStatCode 00 |  |


###### manual oper.  _(bn=5, lv=4)_

|  |  |
|---|---|
| heatCirc1 manOper |  |
| valve 3 |  |
| pump 3 |  |


###### service  _(bn=6, lv=4)_

|  |
|---|
| heatCirc1 service |
| generalVal |
| summer shutdown |
| HCu Adaptation |
| screed drying |
| sensor correction |
| terminal ass. |


###### generalVal  _(bn=1, lv=5)_

|  |  |
|---|---|
| heatCirc1 S-gen.Val |  |
| pump 74225 h |  |
| curDegrDNum 2324 |  |
| histDegrDNo 3754 |  |


###### summer shutdown  _(bn=2, lv=5)_

|  |  |
|---|---|
| heatCirc1 S-summersd |  |
| swOfDate 00.00.00 |  |
| swOfTime 00:00 |  |
| swOnDate 00.00.00 |  |
| swOnTime 00:00 |  |
| swOfDur 0 h |  |


###### HCu Adaptation  _(bn=3, lv=5)_

|  |  |
|---|---|
| heatCirc1 S-HCuAdap |  |
| HC+25 20.0 °C |  |
| HC+20 20.0 °C |  |
| HC+15 22.8 °C |  |
| HC+10 25.4 °C |  |
| HC+5 27.9 °C |  |
| HC+-0 30.3 °C |  |
| HC-5 32.7 °C |  |
| HC-10 35.1 °C |  |
| HC-15 37.4 °C |  |
| HC-20 39.7 °C |  |
| HC-25 42.0 °C |  |
| HC-30 44.3 °C |  |
| HC-35 46.6 °C |  |
| HC-40 48.9 °C |  |
| HC-45 51.1 °C |  |


###### screed drying  _(bn=4, lv=5)_

|  |  |
|---|---|
| heatCirc1 S-screed |  |
| SP-T 0.0 °C |  |
| status off |  |
| intTmr 0.0 h |  |
| numPwFail 0 |  |
| TI-Xw 0 |  |
| reset 0 |  |
| set 0.0 s |  |


###### sensor correction  _(bn=5, lv=5)_

|  |  |
|---|---|
| heatCirc1 S-senCor |  |
| outdoor 0.0 K |  |
| flow 0.0 K |  |


###### terminal ass.  _(bn=6, lv=5)_

|  |  |
|---|---|
| heatCirc1 s-termAss |  |
| room 0 |  |
| outdoor 41 |  |
| flow 18 |  |
| return 0 |  |
| limit 0 |  |
| shift 0 |  |
| SPPoti 0 |  |
| fl-corr 0 |  |
| volFlow 0 |  |
| heatCapa 0 |  |
| htAmount 0 |  |
| system 0 |  |
| key 142 |  |
| oModRC 0 |  |
| oModLoc 151 |  |
| contrOpen 9 |  |
| contrClos 11 |  |
| pump 7 |  |
| troubInd 13 |  |
| VDV 0 |  |


##### heatC. 2  _(bn=2, lv=3)_

|  |
|---|
| heatC. heatC.2 |
| curValue |
| setpoints |
| function |
| status |
| manual oper. |
| service |


###### curValue  _(bn=1, lv=4)_

|  |  |
|---|---|
| heatCirc2 curValue |  |
| outdoor 18.0 °C |  |
| flow 17.1 °C |  |
| delOutT 20.5 °C |  |
| key off |  |
| oModLoc auto |  |


###### setpoints  _(bn=2, lv=4)_

|  |  |
|---|---|
| heatCirc2 setpoints |  |
| roomOT1 45.0 °C |  |
| roomOT2 19.0 °C |  |
| roomOT3 30.0 °C |  |
| roomOT4 27.0 °C |  |
| roomNO 22.0 °C |  |
| roomSNOT 2.0 °C |  |
| hCu-slope 0.5 |  |
| hCu-exp 1.10 |  |
| SP-Flow 18.0 °C |  |


###### function  _(bn=3, lv=4)_

|  |
|---|
| heatCirc2 funct. |
| summer shutdown |
| setpoint limitation |
| controller |
| screed drying |


###### summer shutdown  _(bn=1, lv=5)_

|  |  |
|---|---|
| heatCirc2 F-summersd |  |
| active 0 |  |
| type 1 |  |
| swOfTempOT 18.0 °C |  |
| swOfTempNO 13.0 °C |  |
| swOnTempOT 15.0 °C |  |
| swOnTempNO 11.0 °C |  |


###### setpoint limitation  _(bn=2, lv=5)_

|  |  |
|---|---|
| heatCirc2 F-SP.limit |  |
| active 0 |  |
| minFl 2.0 °C |  |
| maxFl 2.0 °C |  |
| posLim 1400.0 K/h |  |
| negLim 1400.0 K/h |  |
| maxDemFl-T 65.0 °C |  |


###### controller  _(bn=3, lv=5)_

|  |  |
|---|---|
| F-controller |  |
| contrOutp 3 |  |
| longDes heatC. 2 |  |


###### screed drying  _(bn=4, lv=5)_

|  |  |
|---|---|
| heatCirc2 F-screed |  |
| active 0 |  |
| initTemp 25.0 |  |
| dwellInitTemp 1 d |  |
| rateTmp+ 5.0 K |  |
| dwell+ 1 d |  |
| maxTemp 45.0 °C |  |
| dwellMaxTemp 3 d |  |
| rateTmp- 5.0 K |  |
| dwell- 1 d |  |
| optionPwFail 0 |  |
| max-Xw 50.0 K |  |
| dur-Xw 0.5 h |  |


###### status  _(bn=4, lv=4)_

|  |  |
|---|---|
| heatCirc2 status |  |
| opStatus nom. oper. OT2 |  |
| trouble normal |  |
| source timer-OT2 ---------- |  |
| contrOpen off |  |
| contrClos on |  |
| pump off |  |
| troubInd normal |  |
| opStatCode 00080 |  |
| trbStatCode 00 |  |


###### manual oper.  _(bn=5, lv=4)_

|  |  |
|---|---|
| heatCirc2 manOper |  |
| valve 3 |  |
| pump 3 |  |


###### service  _(bn=6, lv=4)_

|  |
|---|
| heatCirc2 service |
| generalVal |
| summer shutdown |
| HCu Adaptation |
| screed drying |
| sensor correction |
| terminal ass. |


###### generalVal  _(bn=1, lv=5)_

|  |  |
|---|---|
| heatCirc2 S-gen.Val |  |
| pump 57093 h |  |
| curDegrDNum 892 |  |
| histDegrDNo 2206 |  |


###### summer shutdown  _(bn=2, lv=5)_

|  |  |
|---|---|
| heatCirc2 S-summersd |  |
| swOfDate 00.00.00 |  |
| swOfTime 00:00 |  |
| swOnDate 00.00.00 |  |
| swOnTime 00:00 |  |
| swOfDur 0 h |  |


###### HCu Adaptation  _(bn=3, lv=5)_

|  |  |
|---|---|
| heatCirc2 S-HCuAdap |  |
| HC+25 56.0 °C |  |
| HC+20 58.5 °C |  |
| HC+15 60.9 °C |  |
| HC+10 63.3 °C |  |
| HC+5 65.6 °C |  |
| HC+-0 68.0 °C |  |
| HC-5 70.3 °C |  |
| HC-10 72.6 °C |  |
| HC-15 74.9 °C |  |
| HC-20 77.1 °C |  |
| HC-25 79.4 °C |  |
| HC-30 81.6 °C |  |
| HC-35 83.8 °C |  |
| HC-40 86.0 °C |  |
| HC-45 88.2 °C |  |


###### screed drying  _(bn=4, lv=5)_

|  |  |
|---|---|
| heatCirc2 S-screed |  |
| SP-T 0.0 °C |  |
| status off |  |
| intTmr 0.0 h |  |
| numPwFail 0 |  |
| TI-Xw 0 |  |
| reset 0 |  |
| set 0.0 s |  |


###### sensor correction  _(bn=5, lv=5)_

|  |  |
|---|---|
| heatCirc2 S-senCor |  |
| outdoor 0.0 K |  |
| flow 0.0 K |  |


###### terminal ass.  _(bn=6, lv=5)_

|  |  |
|---|---|
| heatCirc2 s-termAss |  |
| room 0 |  |
| outdoor 41 |  |
| flow 19 |  |
| return 0 |  |
| limit 0 |  |
| shift 0 |  |
| SPPoti 0 |  |
| fl-corr 0 |  |
| volFlow 0 |  |
| heatCapa 0 |  |
| htAmount 0 |  |
| system 0 |  |
| key 143 |  |
| oModRC 0 |  |
| oModLoc 151 |  |
| contrOpen 1 |  |
| contrClos 3 |  |
| pump 5 |  |
| troubInd 13 |  |
| VDV 0 |  |


#### trend  _(bn=6, lv=2)_

|  |
|---|
| MCR-BMS trend |
| trend 1 |
| trend 2 |
| trend 3 |
| trend 4 |
| trend 5 |
| trend 6 |
| trend 7 |
| trend 8 |
| trend 9 |
| trend 10 |


##### trend 1  _(bn=1, lv=3)_

|  |
|---|
| trend trend 1 |
| curValue |
| function |
| status |
| service |


###### curValue  _(bn=1, lv=4)_

|  |
|---|
| trend 1 curValue |
| trend |


###### trend  _(bn=1, lv=5)_

|  |  |
|---|---|
| trend 1 trend |  |
| curNo.reco 1 |  |
| V1 0 |  |
| V2 0 |  |
| V3 0 |  |
| V4 0 |  |
| V5 0 |  |
| V6 0 |  |
| V7 0 |  |
| V8 0 |  |
| V9 0 |  |
| V10 0 |  |
| V11 0 |  |
| V12 0 |  |
| V13 0 |  |
| V14 0 |  |
| V15 0 |  |
| V16 0 |  |
| V17 0 |  |
| V18 0 |  |
| V19 0 |  |
| V20 0 |  |
| V21 0 |  |
| V22 0 |  |
| V23 0 |  |
| V24 0 |  |
| V25 0 |  |
| V26 0 |  |
| V27 0 |  |
| V28 0 |  |
| V29 0 |  |
| V30 0 |  |
| V31 0 |  |
| V32 0 |  |
| V33 0 |  |
| V34 0 |  |
| V35 0 |  |
| V36 0 |  |
| V37 0 |  |
| V38 0 |  |
| V39 0 |  |
| V40 0 |  |
| V41 0 |  |
| V42 0 |  |
| V43 0 |  |
| V44 0 |  |
| V45 0 |  |
| V46 0 |  |
| V47 0 |  |
| V48 0 |  |
| V49 0 |  |
| V50 0 |  |


###### function  _(bn=2, lv=4)_

|  |
|---|
| trend 1 funct. |
| record |
| controller |


###### record  _(bn=1, lv=5)_

|  |  |
|---|---|
| trend 1 F-record |  |
| active 0 |  |
| intReco 60.0 min |  |


###### controller  _(bn=2, lv=5)_

|  |  |
|---|---|
| trend 1 F-controller |  |
| longDes trend 1 |  |


###### status  _(bn=3, lv=4)_

|  |  |
|---|---|
| trend 1 status |  |
| opStatus not active |  |


###### service  _(bn=4, lv=4)_

|  |
|---|
| trend 1 service |
| record |
| terminal ass. |
| reference/delete |


###### record  _(bn=1, lv=5)_

|  |  |
|---|---|
| trend 1 S-record |  |
| recoValue 0 |  |
| curValue 0 |  |


###### terminal ass.  _(bn=2, lv=5)_

|  |  |
|---|---|
| trend 1 s-termAss |  |
| DPnt 0 |  |


###### reference/delete  _(bn=3, lv=5)_

|  |  |
|---|---|
| trend 1 s-reset |  |
| cold start mem 0 |  |


##### trend 2  _(bn=2, lv=3)_

|  |
|---|
| trend trend 2 |
| curValue |
| function |
| status |
| service |


###### curValue  _(bn=1, lv=4)_

|  |
|---|
| trend 2 curValue |
| trend |


###### trend  _(bn=1, lv=5)_

|  |  |
|---|---|
| trend 2 trend |  |
| curNo.reco 1 |  |
| V1 0 |  |
| V2 0 |  |
| V3 0 |  |
| V4 0 |  |
| V5 0 |  |
| V6 0 |  |
| V7 0 |  |
| V8 0 |  |
| V9 0 |  |
| V10 0 |  |
| V11 0 |  |
| V12 0 |  |
| V13 0 |  |
| V14 0 |  |
| V15 0 |  |
| V16 0 |  |
| V17 0 |  |
| V18 0 |  |
| V19 0 |  |
| V20 0 |  |
| V21 0 |  |
| V22 0 |  |
| V23 0 |  |
| V24 0 |  |
| V25 0 |  |
| V26 0 |  |
| V27 0 |  |
| V28 0 |  |
| V29 0 |  |
| V30 0 |  |
| V31 0 |  |
| V32 0 |  |
| V33 0 |  |
| V34 0 |  |
| V35 0 |  |
| V36 0 |  |
| V37 0 |  |
| V38 0 |  |
| V39 0 |  |
| V40 0 |  |
| V41 0 |  |
| V42 0 |  |
| V43 0 |  |
| V44 0 |  |
| V45 0 |  |
| V46 0 |  |
| V47 0 |  |
| V48 0 |  |
| V49 0 |  |
| V50 0 |  |


###### function  _(bn=2, lv=4)_

|  |
|---|
| trend 2 funct. |
| record |
| controller |


###### record  _(bn=1, lv=5)_

|  |  |
|---|---|
| trend 2 F-record |  |
| active 0 |  |
| intReco 60.0 min |  |


###### controller  _(bn=2, lv=5)_

|  |  |
|---|---|
| trend 2 F-controller |  |
| longDes trend 2 |  |


###### status  _(bn=3, lv=4)_

|  |  |
|---|---|
| trend 2 status |  |
| opStatus not active |  |


###### service  _(bn=4, lv=4)_

|  |
|---|
| trend 2 service |
| record |
| terminal ass. |
| reference/delete |


###### record  _(bn=1, lv=5)_

|  |  |
|---|---|
| trend 2 S-record |  |
| recoValue 0 |  |
| curValue 0 |  |


###### terminal ass.  _(bn=2, lv=5)_

|  |  |
|---|---|
| trend 2 s-termAss |  |
| DPnt 0 |  |


###### reference/delete  _(bn=3, lv=5)_

|  |  |
|---|---|
| trend 2 s-reset |  |
| cold start mem 0 |  |


##### trend 3  _(bn=3, lv=3)_

|  |
|---|
| trend trend 3 |
| curValue |
| function |
| status |
| service |


###### curValue  _(bn=1, lv=4)_

|  |
|---|
| trend 3 curValue |
| trend |


###### trend  _(bn=1, lv=5)_

|  |  |
|---|---|
| trend 3 trend |  |
| curNo.reco 1 |  |
| V1 0 |  |
| V2 0 |  |
| V3 0 |  |
| V4 0 |  |
| V5 0 |  |
| V6 0 |  |
| V7 0 |  |
| V8 0 |  |
| V9 0 |  |
| V10 0 |  |
| V11 0 |  |
| V12 0 |  |
| V13 0 |  |
| V14 0 |  |
| V15 0 |  |
| V16 0 |  |
| V17 0 |  |
| V18 0 |  |
| V19 0 |  |
| V20 0 |  |
| V21 0 |  |
| V22 0 |  |
| V23 0 |  |
| V24 0 |  |
| V25 0 |  |
| V26 0 |  |
| V27 0 |  |
| V28 0 |  |
| V29 0 |  |
| V30 0 |  |
| V31 0 |  |
| V32 0 |  |
| V33 0 |  |
| V34 0 |  |
| V35 0 |  |
| V36 0 |  |
| V37 0 |  |
| V38 0 |  |
| V39 0 |  |
| V40 0 |  |
| V41 0 |  |
| V42 0 |  |
| V43 0 |  |
| V44 0 |  |
| V45 0 |  |
| V46 0 |  |
| V47 0 |  |
| V48 0 |  |
| V49 0 |  |
| V50 0 |  |


###### function  _(bn=2, lv=4)_

|  |
|---|
| trend 3 funct. |
| record |
| controller |


###### record  _(bn=1, lv=5)_

|  |  |
|---|---|
| trend 3 F-record |  |
| active 0 |  |
| intReco 60.0 min |  |


###### controller  _(bn=2, lv=5)_

|  |  |
|---|---|
| trend 3 F-controller |  |
| longDes trend 3 |  |


###### status  _(bn=3, lv=4)_

|  |  |
|---|---|
| trend 3 status |  |
| opStatus not active |  |


###### service  _(bn=4, lv=4)_

|  |
|---|
| trend 3 service |
| record |
| terminal ass. |
| reference/delete |


###### record  _(bn=1, lv=5)_

|  |  |
|---|---|
| trend 3 S-record |  |
| recoValue 0 |  |
| curValue 0 |  |


###### terminal ass.  _(bn=2, lv=5)_

|  |  |
|---|---|
| trend 3 s-termAss |  |
| DPnt 0 |  |


###### reference/delete  _(bn=3, lv=5)_

|  |  |
|---|---|
| trend 3 s-reset |  |
| cold start mem 0 |  |


##### trend 4  _(bn=4, lv=3)_

|  |
|---|
| trend trend 4 |
| curValue |
| function |
| status |
| service |


###### curValue  _(bn=1, lv=4)_

|  |
|---|
| trend 4 curValue |
| trend |


###### trend  _(bn=1, lv=5)_

|  |  |
|---|---|
| trend 4 trend |  |
| curNo.reco 1 |  |
| V1 0 |  |
| V2 0 |  |
| V3 0 |  |
| V4 0 |  |
| V5 0 |  |
| V6 0 |  |
| V7 0 |  |
| V8 0 |  |
| V9 0 |  |
| V10 0 |  |
| V11 0 |  |
| V12 0 |  |
| V13 0 |  |
| V14 0 |  |
| V15 0 |  |
| V16 0 |  |
| V17 0 |  |
| V18 0 |  |
| V19 0 |  |
| V20 0 |  |
| V21 0 |  |
| V22 0 |  |
| V23 0 |  |
| V24 0 |  |
| V25 0 |  |
| V26 0 |  |
| V27 0 |  |
| V28 0 |  |
| V29 0 |  |
| V30 0 |  |
| V31 0 |  |
| V32 0 |  |
| V33 0 |  |
| V34 0 |  |
| V35 0 |  |
| V36 0 |  |
| V37 0 |  |
| V38 0 |  |
| V39 0 |  |
| V40 0 |  |
| V41 0 |  |
| V42 0 |  |
| V43 0 |  |
| V44 0 |  |
| V45 0 |  |
| V46 0 |  |
| V47 0 |  |
| V48 0 |  |
| V49 0 |  |
| V50 0 |  |


###### function  _(bn=2, lv=4)_

|  |
|---|
| trend 4 funct. |
| record |
| controller |


###### record  _(bn=1, lv=5)_

|  |  |
|---|---|
| trend 4 F-record |  |
| active 0 |  |
| intReco 60.0 min |  |


###### controller  _(bn=2, lv=5)_

|  |  |
|---|---|
| trend 4 F-controller |  |
| longDes trend 4 |  |


###### status  _(bn=3, lv=4)_

|  |  |
|---|---|
| trend 4 status |  |
| opStatus not active |  |


###### service  _(bn=4, lv=4)_

|  |
|---|
| trend 4 service |
| record |
| terminal ass. |
| reference/delete |


###### record  _(bn=1, lv=5)_

|  |  |
|---|---|
| trend 4 S-record |  |
| recoValue 0 |  |
| curValue 0 |  |


###### terminal ass.  _(bn=2, lv=5)_

|  |  |
|---|---|
| trend 4 s-termAss |  |
| DPnt 0 |  |


###### reference/delete  _(bn=3, lv=5)_

|  |  |
|---|---|
| trend 4 s-reset |  |
| cold start mem 0 |  |


##### trend 5  _(bn=5, lv=3)_

|  |
|---|
| trend trend 5 |
| curValue |
| function |
| status |
| service |


###### curValue  _(bn=1, lv=4)_

|  |
|---|
| trend 5 curValue |
| trend |


###### trend  _(bn=1, lv=5)_

|  |  |
|---|---|
| trend 5 trend |  |
| curNo.reco 1 |  |
| V1 0 |  |
| V2 0 |  |
| V3 0 |  |
| V4 0 |  |
| V5 0 |  |
| V6 0 |  |
| V7 0 |  |
| V8 0 |  |
| V9 0 |  |
| V10 0 |  |
| V11 0 |  |
| V12 0 |  |
| V13 0 |  |
| V14 0 |  |
| V15 0 |  |
| V16 0 |  |
| V17 0 |  |
| V18 0 |  |
| V19 0 |  |
| V20 0 |  |
| V21 0 |  |
| V22 0 |  |
| V23 0 |  |
| V24 0 |  |
| V25 0 |  |
| V26 0 |  |
| V27 0 |  |
| V28 0 |  |
| V29 0 |  |
| V30 0 |  |
| V31 0 |  |
| V32 0 |  |
| V33 0 |  |
| V34 0 |  |
| V35 0 |  |
| V36 0 |  |
| V37 0 |  |
| V38 0 |  |
| V39 0 |  |
| V40 0 |  |
| V41 0 |  |
| V42 0 |  |
| V43 0 |  |
| V44 0 |  |
| V45 0 |  |
| V46 0 |  |
| V47 0 |  |
| V48 0 |  |
| V49 0 |  |
| V50 0 |  |


###### function  _(bn=2, lv=4)_

|  |
|---|
| trend 5 funct. |
| record |
| controller |


###### record  _(bn=1, lv=5)_

|  |  |
|---|---|
| trend 5 F-record |  |
| active 0 |  |
| intReco 60.0 min |  |


###### controller  _(bn=2, lv=5)_

|  |  |
|---|---|
| trend 5 F-controller |  |
| longDes trend 5 |  |


###### status  _(bn=3, lv=4)_

|  |  |
|---|---|
| trend 5 status |  |
| opStatus not active |  |


###### service  _(bn=4, lv=4)_

|  |
|---|
| trend 5 service |
| record |
| terminal ass. |
| reference/delete |


###### record  _(bn=1, lv=5)_

|  |  |
|---|---|
| trend 5 S-record |  |
| recoValue 0 |  |
| curValue 0 |  |


###### terminal ass.  _(bn=2, lv=5)_

|  |  |
|---|---|
| trend 5 s-termAss |  |
| DPnt 0 |  |


###### reference/delete  _(bn=3, lv=5)_

|  |  |
|---|---|
| trend 5 s-reset |  |
| cold start mem 0 |  |


##### trend 6  _(bn=6, lv=3)_

|  |
|---|
| trend trend 6 |
| curValue |
| function |
| status |
| service |


###### curValue  _(bn=1, lv=4)_

|  |
|---|
| trend 6 curValue |
| trend |


###### trend  _(bn=1, lv=5)_

|  |  |
|---|---|
| trend 6 trend |  |
| curNo.reco 1 |  |
| V1 0 |  |
| V2 0 |  |
| V3 0 |  |
| V4 0 |  |
| V5 0 |  |
| V6 0 |  |
| V7 0 |  |
| V8 0 |  |
| V9 0 |  |
| V10 0 |  |
| V11 0 |  |
| V12 0 |  |
| V13 0 |  |
| V14 0 |  |
| V15 0 |  |
| V16 0 |  |
| V17 0 |  |
| V18 0 |  |
| V19 0 |  |
| V20 0 |  |
| V21 0 |  |
| V22 0 |  |
| V23 0 |  |
| V24 0 |  |
| V25 0 |  |
| V26 0 |  |
| V27 0 |  |
| V28 0 |  |
| V29 0 |  |
| V30 0 |  |
| V31 0 |  |
| V32 0 |  |
| V33 0 |  |
| V34 0 |  |
| V35 0 |  |
| V36 0 |  |
| V37 0 |  |
| V38 0 |  |
| V39 0 |  |
| V40 0 |  |
| V41 0 |  |
| V42 0 |  |
| V43 0 |  |
| V44 0 |  |
| V45 0 |  |
| V46 0 |  |
| V47 0 |  |
| V48 0 |  |
| V49 0 |  |
| V50 0 |  |


###### function  _(bn=2, lv=4)_

|  |
|---|
| trend 6 funct. |
| record |
| controller |


###### record  _(bn=1, lv=5)_

|  |  |
|---|---|
| trend 6 F-record |  |
| active 0 |  |
| intReco 60.0 min |  |


###### controller  _(bn=2, lv=5)_

|  |  |
|---|---|
| trend 6 F-controller |  |
| longDes trend 6 |  |


###### status  _(bn=3, lv=4)_

|  |  |
|---|---|
| trend 6 status |  |
| opStatus not active |  |


###### service  _(bn=4, lv=4)_

|  |
|---|
| trend 6 service |
| record |
| terminal ass. |
| reference/delete |


###### record  _(bn=1, lv=5)_

|  |  |
|---|---|
| trend 6 S-record |  |
| recoValue 0 |  |
| curValue 0 |  |


###### terminal ass.  _(bn=2, lv=5)_

|  |  |
|---|---|
| trend 6 s-termAss |  |
| DPnt 0 |  |


###### reference/delete  _(bn=3, lv=5)_

|  |  |
|---|---|
| trend 6 s-reset |  |
| cold start mem 0 |  |


##### trend 7  _(bn=7, lv=3)_

|  |
|---|
| trend trend 7 |
| curValue |
| function |
| status |
| service |


###### curValue  _(bn=1, lv=4)_

|  |
|---|
| trend 7 curValue |
| trend |


###### trend  _(bn=1, lv=5)_

|  |  |
|---|---|
| trend 7 trend |  |
| curNo.reco 1 |  |
| V1 0 |  |
| V2 0 |  |
| V3 0 |  |
| V4 0 |  |
| V5 0 |  |
| V6 0 |  |
| V7 0 |  |
| V8 0 |  |
| V9 0 |  |
| V10 0 |  |
| V11 0 |  |
| V12 0 |  |
| V13 0 |  |
| V14 0 |  |
| V15 0 |  |
| V16 0 |  |
| V17 0 |  |
| V18 0 |  |
| V19 0 |  |
| V20 0 |  |
| V21 0 |  |
| V22 0 |  |
| V23 0 |  |
| V24 0 |  |
| V25 0 |  |
| V26 0 |  |
| V27 0 |  |
| V28 0 |  |
| V29 0 |  |
| V30 0 |  |
| V31 0 |  |
| V32 0 |  |
| V33 0 |  |
| V34 0 |  |
| V35 0 |  |
| V36 0 |  |
| V37 0 |  |
| V38 0 |  |
| V39 0 |  |
| V40 0 |  |
| V41 0 |  |
| V42 0 |  |
| V43 0 |  |
| V44 0 |  |
| V45 0 |  |
| V46 0 |  |
| V47 0 |  |
| V48 0 |  |
| V49 0 |  |
| V50 0 |  |


###### function  _(bn=2, lv=4)_

|  |
|---|
| trend 7 funct. |
| record |
| controller |


###### record  _(bn=1, lv=5)_

|  |  |
|---|---|
| trend 7 F-record |  |
| active 0 |  |
| intReco 60.0 min |  |


###### controller  _(bn=2, lv=5)_

|  |  |
|---|---|
| trend 7 F-controller |  |
| longDes trend 7 |  |


###### status  _(bn=3, lv=4)_

|  |  |
|---|---|
| trend 7 status |  |
| opStatus not active |  |


###### service  _(bn=4, lv=4)_

|  |
|---|
| trend 7 service |
| record |
| terminal ass. |
| reference/delete |


###### record  _(bn=1, lv=5)_

|  |  |
|---|---|
| trend 7 S-record |  |
| recoValue 0 |  |
| curValue 0 |  |


###### terminal ass.  _(bn=2, lv=5)_

|  |  |
|---|---|
| trend 7 s-termAss |  |
| DPnt 0 |  |


###### reference/delete  _(bn=3, lv=5)_

|  |  |
|---|---|
| trend 7 s-reset |  |
| cold start mem 0 |  |


##### trend 8  _(bn=8, lv=3)_

|  |
|---|
| trend trend 8 |
| curValue |
| function |
| status |
| service |


###### curValue  _(bn=1, lv=4)_

|  |
|---|
| trend 8 curValue |
| trend |


###### trend  _(bn=1, lv=5)_

|  |  |
|---|---|
| trend 8 trend |  |
| curNo.reco 1 |  |
| V1 0 |  |
| V2 0 |  |
| V3 0 |  |
| V4 0 |  |
| V5 0 |  |
| V6 0 |  |
| V7 0 |  |
| V8 0 |  |
| V9 0 |  |
| V10 0 |  |
| V11 0 |  |
| V12 0 |  |
| V13 0 |  |
| V14 0 |  |
| V15 0 |  |
| V16 0 |  |
| V17 0 |  |
| V18 0 |  |
| V19 0 |  |
| V20 0 |  |
| V21 0 |  |
| V22 0 |  |
| V23 0 |  |
| V24 0 |  |
| V25 0 |  |
| V26 0 |  |
| V27 0 |  |
| V28 0 |  |
| V29 0 |  |
| V30 0 |  |
| V31 0 |  |
| V32 0 |  |
| V33 0 |  |
| V34 0 |  |
| V35 0 |  |
| V36 0 |  |
| V37 0 |  |
| V38 0 |  |
| V39 0 |  |
| V40 0 |  |
| V41 0 |  |
| V42 0 |  |
| V43 0 |  |
| V44 0 |  |
| V45 0 |  |
| V46 0 |  |
| V47 0 |  |
| V48 0 |  |
| V49 0 |  |
| V50 0 |  |


###### function  _(bn=2, lv=4)_

|  |
|---|
| trend 8 funct. |
| record |
| controller |


###### record  _(bn=1, lv=5)_

|  |  |
|---|---|
| trend 8 F-record |  |
| active 0 |  |
| intReco 60.0 min |  |


###### controller  _(bn=2, lv=5)_

|  |  |
|---|---|
| trend 8 F-controller |  |
| longDes trend 8 |  |


###### status  _(bn=3, lv=4)_

|  |  |
|---|---|
| trend 8 status |  |
| opStatus not active |  |


###### service  _(bn=4, lv=4)_

|  |
|---|
| trend 8 service |
| record |
| terminal ass. |
| reference/delete |


###### record  _(bn=1, lv=5)_

|  |  |
|---|---|
| trend 8 S-record |  |
| recoValue 0 |  |
| curValue 0 |  |


###### terminal ass.  _(bn=2, lv=5)_

|  |  |
|---|---|
| trend 8 s-termAss |  |
| DPnt 0 |  |


###### reference/delete  _(bn=3, lv=5)_

|  |  |
|---|---|
| trend 8 s-reset |  |
| cold start mem 0 |  |


##### trend 9  _(bn=9, lv=3)_

|  |
|---|
| trend trend 9 |
| curValue |
| function |
| status |
| service |


###### curValue  _(bn=1, lv=4)_

|  |
|---|
| trend 9 curValue |
| trend |


###### trend  _(bn=1, lv=5)_

|  |  |
|---|---|
| trend 9 trend |  |
| curNo.reco 1 |  |
| V1 0 |  |
| V2 0 |  |
| V3 0 |  |
| V4 0 |  |
| V5 0 |  |
| V6 0 |  |
| V7 0 |  |
| V8 0 |  |
| V9 0 |  |
| V10 0 |  |
| V11 0 |  |
| V12 0 |  |
| V13 0 |  |
| V14 0 |  |
| V15 0 |  |
| V16 0 |  |
| V17 0 |  |
| V18 0 |  |
| V19 0 |  |
| V20 0 |  |
| V21 0 |  |
| V22 0 |  |
| V23 0 |  |
| V24 0 |  |
| V25 0 |  |
| V26 0 |  |
| V27 0 |  |
| V28 0 |  |
| V29 0 |  |
| V30 0 |  |
| V31 0 |  |
| V32 0 |  |
| V33 0 |  |
| V34 0 |  |
| V35 0 |  |
| V36 0 |  |
| V37 0 |  |
| V38 0 |  |
| V39 0 |  |
| V40 0 |  |
| V41 0 |  |
| V42 0 |  |
| V43 0 |  |
| V44 0 |  |
| V45 0 |  |
| V46 0 |  |
| V47 0 |  |
| V48 0 |  |
| V49 0 |  |
| V50 0 |  |


###### function  _(bn=2, lv=4)_

|  |
|---|
| trend 9 funct. |
| record |
| controller |


###### record  _(bn=1, lv=5)_

|  |  |
|---|---|
| trend 9 F-record |  |
| active 0 |  |
| intReco 60.0 min |  |


###### controller  _(bn=2, lv=5)_

|  |  |
|---|---|
| trend 9 F-controller |  |
| longDes trend 9 |  |


###### status  _(bn=3, lv=4)_

|  |  |
|---|---|
| trend 9 status |  |
| opStatus not active |  |


###### service  _(bn=4, lv=4)_

|  |
|---|
| trend 9 service |
| record |
| terminal ass. |
| reference/delete |


###### record  _(bn=1, lv=5)_

|  |  |
|---|---|
| trend 9 S-record |  |
| recoValue 0 |  |
| curValue 0 |  |


###### terminal ass.  _(bn=2, lv=5)_

|  |  |
|---|---|
| trend 9 s-termAss |  |
| DPnt 0 |  |


###### reference/delete  _(bn=3, lv=5)_

|  |  |
|---|---|
| trend 9 s-reset |  |
| cold start mem 0 |  |


##### trend 10  _(bn=10, lv=3)_

|  |
|---|
| trend trend 10 |
| curValue |
| function |
| status |
| service |


###### curValue  _(bn=1, lv=4)_

|  |
|---|
| trend 10 curValue |
| trend |


###### trend  _(bn=1, lv=5)_

|  |  |
|---|---|
| trend 10 trend |  |
| curNo.reco 1 |  |
| V1 0 |  |
| V2 0 |  |
| V3 0 |  |
| V4 0 |  |
| V5 0 |  |
| V6 0 |  |
| V7 0 |  |
| V8 0 |  |
| V9 0 |  |
| V10 0 |  |
| V11 0 |  |
| V12 0 |  |
| V13 0 |  |
| V14 0 |  |
| V15 0 |  |
| V16 0 |  |
| V17 0 |  |
| V18 0 |  |
| V19 0 |  |
| V20 0 |  |
| V21 0 |  |
| V22 0 |  |
| V23 0 |  |
| V24 0 |  |
| V25 0 |  |
| V26 0 |  |
| V27 0 |  |
| V28 0 |  |
| V29 0 |  |
| V30 0 |  |
| V31 0 |  |
| V32 0 |  |
| V33 0 |  |
| V34 0 |  |
| V35 0 |  |
| V36 0 |  |
| V37 0 |  |
| V38 0 |  |
| V39 0 |  |
| V40 0 |  |
| V41 0 |  |
| V42 0 |  |
| V43 0 |  |
| V44 0 |  |
| V45 0 |  |
| V46 0 |  |
| V47 0 |  |
| V48 0 |  |
| V49 0 |  |
| V50 0 |  |


###### function  _(bn=2, lv=4)_

|  |
|---|
| trend 10 funct. |
| record |
| controller |


###### record  _(bn=1, lv=5)_

|  |  |
|---|---|
| trend 10 F-record |  |
| active 0 |  |
| intReco 60.0 min |  |


###### controller  _(bn=2, lv=5)_

|  |  |
|---|---|
| F-controller |  |
| longDes trend 10 |  |


###### status  _(bn=3, lv=4)_

|  |  |
|---|---|
| trend 10 status |  |
| opStatus not active |  |


###### service  _(bn=4, lv=4)_

|  |
|---|
| trend 10 service |
| record |
| terminal ass. |
| reference/delete |


###### record  _(bn=1, lv=5)_

|  |  |
|---|---|
| trend 10 S-record |  |
| recoValue 0 |  |
| curValue 0 |  |


###### terminal ass.  _(bn=2, lv=5)_

|  |  |
|---|---|
| trend 10 s-termAss |  |
| DPnt 0 |  |


###### reference/delete  _(bn=3, lv=5)_

|  |  |
|---|---|
| trend 10 s-reset |  |
| cold start mem 0 |  |


#### photovoltaics  _(bn=7, lv=2)_

|  |
|---|
| MCR-BMS pv |
| curValue |
| setpoints |
| function |
| status |
| service |


##### curValue  _(bn=1, lv=3)_

|  |  |
|---|---|
| curValue |  |
| no parameter |  |


##### setpoints  _(bn=2, lv=3)_

|  |  |
|---|---|
| setpoints |  |
| currDemHC 2 °C |  |
| currDemDHW 2 °C |  |


##### function  _(bn=3, lv=3)_

|  |
|---|
| funct. |
| temperatures |
| sequence timing |
| type photovoltaics |


###### temperatures  _(bn=1, lv=4)_

|  |  |
|---|---|
| F-temp |  |
| dem-HC 50 °C |  |
| dem-DHW 50 °C |  |


###### sequence timing  _(bn=2, lv=4)_

|  |  |
|---|---|
| F-time |  |
| minSwOfTm 10.0 min |  |


###### type photovoltaics  _(bn=3, lv=4)_

|  |  |
|---|---|
| F-type |  |
| type-Pv 1 |  |
| dem-HC 1 |  |
| dem-DHW 1 |  |


##### status  _(bn=4, lv=3)_

|  |  |
|---|---|
| status |  |
| opStatus not active/off |  |
| trouble normal |  |
| opStatCode 00 |  |
| trbStatCode 00 |  |


##### service  _(bn=5, lv=3)_

|  |
|---|
| service |
| sequence timing |
| terminal ass. |


###### sequence timing  _(bn=1, lv=4)_

|  |  |
|---|---|
| S-time |  |
| minSwOfTm 0.0 min |  |


###### terminal ass.  _(bn=2, lv=4)_

|  |  |
|---|---|
| s-termAss |  |
| rel-pv 0 |  |


#### Smart Grid  _(bn=8, lv=2)_

|  |
|---|
| MCR-BMS SG |
| curValue |
| setpoints |
| function |
| status |
| service |


##### curValue  _(bn=1, lv=3)_

|  |  |
|---|---|
| curValue |  |
| no parameter |  |


##### setpoints  _(bn=2, lv=3)_

|  |  |
|---|---|
| setpoints |  |
| currDemHC 2.0 °C |  |
| currDemDHW 2.0 °C |  |


##### function  _(bn=3, lv=3)_

|  |
|---|
| funct. |
| operating state 3 |
| operating state 4 |


###### operating state 3  _(bn=1, lv=4)_

|  |  |
|---|---|
| F-opState3 |  |
| boost-hCu 10 % |  |
| boost-DHW 10 % |  |


###### operating state 4  _(bn=2, lv=4)_

|  |  |
|---|---|
| F-opState4 |  |
| dem-HC 50 °C |  |
| dem-DHW 50 °C |  |


##### status  _(bn=4, lv=3)_

|  |  |
|---|---|
| status |  |
| opStatus not active/off |  |
| trouble normal |  |
| operating state 0 |  |
| opStatCode 00 |  |
| trbStatCode 00 |  |


##### service  _(bn=5, lv=3)_

|  |
|---|
| service |
| terminal ass. |


###### terminal ass.  _(bn=1, lv=4)_

|  |  |
|---|---|
| s-termAss |  |
| inp1 0 |  |
| Inp2 0 |  |


#### Extended configur.  _(bn=9, lv=2)_

|  |
|---|
| MCR-BMS ExtdConf. |
| hCu1 room compens. |
| hCu2 room compens. |
| HP Bivalence |
| domHotWater solar |
| buffer solar |
| buffer addHS/fireside |
| photovoltaics |
| Smart Grid |


##### hCu1 room compens.  _(bn=1, lv=3)_

|  |  |
|---|---|
| ExtdConf. hCu1room |  |
| room compens. 0 |  |


##### hCu2 room compens.  _(bn=2, lv=3)_

|  |  |
|---|---|
| ExtdConf. hCu2room |  |
| room compens. 0 |  |


##### HP Bivalence  _(bn=3, lv=3)_

|  |  |
|---|---|
| ExtdConf. HP-Biv |  |
| HP-Biv 0 |  |


##### domHotWater solar  _(bn=4, lv=3)_

|  |  |
|---|---|
| ExtdConf. DHW-solar |  |
| solColl 0 |  |


##### buffer solar  _(bn=5, lv=3)_

|  |  |
|---|---|
| Erw.Konf. buf-solar |  |
| solColl 0 |  |


##### buffer addHS/fireside  _(bn=6, lv=3)_

|  |  |
|---|---|
| ExtdConf. buf-addHS |  |
| addHS-Fl 0 |  |


##### photovoltaics  _(bn=7, lv=3)_

|  |  |
|---|---|
| ExtdConf. PV |  |
| type-Pv 1 |  |
| rel-pv 0 |  |
| minSwOfTm 10.0 min |  |
| dem-DHW 1 |  |
| dem-DHW 50 °C |  |
| dem-HC 1 |  |
| dem-HC 50 °C |  |


##### Smart Grid  _(bn=8, lv=3)_

|  |  |
|---|---|
| ExtdConf. SG |  |
| inp1 0 |  |
| Inp2 0 |  |


### interfaces  _(bn=3, lv=1)_

|  |
|---|
| interfaces |
| Ethernet |
| heatpumps |


#### Ethernet  _(bn=1, lv=2)_

|  |  |
|---|---|
| interface ethernet |  |
| active 1 |  |
| host name hpm-800B7F |  |
| MAC-adr 00:1F:FC:80:0B:7F |  |
| DHCPC 0 |  |
| IP-no 192.168.1.11 |  |
| netMask 255.255.255.0 |  |
| defaultGW 192.168.178.1 |  |
| nameserver 192.168.178.1 |  |
| Link LF |  |


#### heatpumps  _(bn=2, lv=2)_

|  |
|---|
| interface. HP |
| general char. val. |
| heatpump 1 |


##### general char. val.  _(bn=1, lv=3)_

|  |  |
|---|---|
| HP gen.val |  |
| no parameter |  |


##### heatpump 1  _(bn=2, lv=3)_

|  |  |
|---|---|
| HP HP1 |  |
| HGS_cycl_c_running |  |
| HCS_connection |  |


### configuration  _(bn=4, lv=1)_

|  |
|---|
| configuration |
| inputs |
| outputs |
| switch |


#### inputs  _(bn=1, lv=2)_

|  |
|---|
| config. inputs |
| term.17 sensor |
| term.18 sensor |
| term.19 sensor |
| term.20 sensor |
| term.21 sensor |
| term.22 sensor |
| term.23 sensor |
| term.24 sensor |
| term.25 meter/mess. |
| term.26 meter/mess. |
| term.27 0-10V |
| term.28 0-10V |


##### term.17 sensor  _(bn=1, lv=3)_

|  |  |
|---|---|
| term.17 sensor |  |
| termMode 0 |  |
| typeSensor Pt1000 |  |
| rawVal 2.000 kOhm |  |
| smTConst 1 s |  |
| termVal 0.0 °C |  |


##### term.18 sensor  _(bn=2, lv=3)_

|  |  |
|---|---|
| term.18 sensor |  |
| termMode 0 |  |
| typeSensor Pt1000 |  |
| rawVal 1.083 kOhm |  |
| smTConst 1 s |  |
| termVal 21.3 °C |  |


##### term.19 sensor  _(bn=3, lv=3)_

|  |  |
|---|---|
| term.19 sensor |  |
| termMode 0 |  |
| typeSensor Pt1000 |  |
| rawVal 1.066 kOhm |  |
| smTConst 1 s |  |
| termVal 17.1 °C |  |


##### term.20 sensor  _(bn=4, lv=3)_

|  |  |
|---|---|
| term.20 sensor |  |
| termMode 0 |  |
| typeSensor Pt1000 |  |
| rawVal 2.000 kOhm |  |
| smTConst 1 s |  |
| termVal 0.0 °C |  |


##### term.21 sensor  _(bn=5, lv=3)_

|  |  |
|---|---|
| term.21 sensor |  |
| termMode 0 |  |
| typeSensor Pt1000 |  |
| rawVal 2.000 kOhm |  |
| smTConst 1 s |  |
| termVal 0.0 °C |  |


##### term.22 sensor  _(bn=6, lv=3)_

|  |  |
|---|---|
| term.22 sensor |  |
| termMode 0 |  |
| typeSensor Pt1000 |  |
| rawVal 1.133 kOhm |  |
| smTConst 1 s |  |
| termVal 34.3 °C |  |


##### term.23 sensor  _(bn=7, lv=3)_

|  |  |
|---|---|
| term.23 sensor |  |
| termMode 0 |  |
| typeSensor Pt1000 |  |
| rawVal 2.000 kOhm |  |
| smTConst 1 s |  |
| termVal 0.0 °C |  |


##### term.24 sensor  _(bn=8, lv=3)_

|  |  |
|---|---|
| term.24 sensor |  |
| termMode 0 |  |
| typeSensor Pt1000 |  |
| rawVal 2.000 kOhm |  |
| smTConst 1 s |  |
| termVal 0.0 °C |  |


##### term.25 meter/mess.  _(bn=9, lv=3)_

|  |  |
|---|---|
| term.25 meter/mess. |  |
| termType 4 |  |
| rawValue 0 |  |
| curStat 1 |  |
| termVal 0 |  |


##### term.26 meter/mess.  _(bn=10, lv=3)_

|  |  |
|---|---|
| term.26 meter/mess. |  |
| termType 4 |  |
| rawValue 0 |  |
| curStat 1 |  |
| termVal 0 |  |


##### term.27 0-10V  _(bn=11, lv=3)_

|  |  |
|---|---|
| term.27 0-10V |  |
| termMode 0 |  |
| raw value 0.015 V |  |
| EPsrc1 0.0 V |  |
| EPsrc2 10.0 V |  |
| unit 150 |  |
| OPntTl1 0.0 % |  |
| OPntTl2 100.0 % |  |
| smTConst 1 s |  |
| termVal 0.1 % |  |


##### term.28 0-10V  _(bn=12, lv=3)_

|  |  |
|---|---|
| term.28 0-10V |  |
| termMode 0 |  |
| raw value 0.000 V |  |
| EPsrc1 0.0 V |  |
| EPsrc2 10.0 V |  |
| unit 150 |  |
| OPntTl1 0.0 % |  |
| OPntTl2 100.0 % |  |
| smTConst 1 s |  |
| termVal 0.0 % |  |


#### outputs  _(bn=2, lv=2)_

|  |
|---|
| config. outputs |
| term01 relais-outp |
| term03 relais-outp |
| term05 relais-outp |
| term07 relais-outp |
| term09 relais-outp |
| term11 relais-outp |
| term13 relais-outp |
| term27 10V-outp. |
| term28 10V-outp. |


##### term01 relais-outp  _(bn=1, lv=3)_

|  |  |
|---|---|
| term01 relais-outp |  |
| srcVal 0 |  |
| curStat 1 |  |
| termVal 0 |  |


##### term03 relais-outp  _(bn=2, lv=3)_

|  |  |
|---|---|
| term03 relais-outp |  |
| srcVal 1 |  |
| curStat 1 |  |
| termVal 1 |  |


##### term05 relais-outp  _(bn=3, lv=3)_

|  |  |
|---|---|
| term05 relais-outp |  |
| srcVal 0 |  |
| curStat 1 |  |
| termVal 0 |  |


##### term07 relais-outp  _(bn=4, lv=3)_

|  |  |
|---|---|
| term07 relais-outp |  |
| srcVal 1 |  |
| curStat 1 |  |
| termVal 1 |  |


##### term09 relais-outp  _(bn=5, lv=3)_

|  |  |
|---|---|
| term09 relais-outp |  |
| srcVal 0 |  |
| curStat 1 |  |
| termVal 0 |  |


##### term11 relais-outp  _(bn=6, lv=3)_

|  |  |
|---|---|
| term11 relais-outp |  |
| srcVal 1 |  |
| curStat 1 |  |
| termVal 1 |  |


##### term13 relais-outp  _(bn=7, lv=3)_

|  |  |
|---|---|
| term13 relais-outp |  |
| srcVal 0 |  |
| curStat 1 |  |
| termVal 0 |  |


##### term27 10V-outp.  _(bn=8, lv=3)_

|  |  |
|---|---|
| term27 10V-outp. |  |
| active 0 |  |
| srcVal 0 |  |
| EPsrc1 0 |  |
| EPsrc2 100 |  |
| OPntTl1 0.0 V |  |
| OPntTl2 10.0 V |  |
| termVal 0.0 V |  |


##### term28 10V-outp.  _(bn=9, lv=3)_

|  |  |
|---|---|
| term28 10V-outp. |  |
| active 0 |  |
| srcVal 0 |  |
| EPsrc1 0 |  |
| EPsrc2 100 |  |
| OPntTl1 0.0 V |  |
| OPntTl2 10.0 V |  |
| termVal 0.0 V |  |


#### switch  _(bn=3, lv=2)_

|  |
|---|
| config. switch |
| term.151 oMod-Sw |
| term.152 MS-W-pump1 |
| term.153 MS-W-pump2 |
| term.154 MS-W-pump3 |


##### term.151 oMod-Sw  _(bn=1, lv=3)_

|  |  |
|---|---|
| term.151 oMod-Sw |  |
| active 1 |  |
| rawValue 1 |  |
| defValue 0 |  |
| termVal auto |  |


##### term.152 MS-W-pump1  _(bn=2, lv=3)_

|  |  |
|---|---|
| term.152 MS-W-pump1 |  |
| rawValue 1 |  |
| termVal auto |  |


##### term.153 MS-W-pump2  _(bn=3, lv=3)_

|  |  |
|---|---|
| term.153 MS-W-pump2 |  |
| rawValue 1 |  |
| termVal auto |  |


##### term.154 MS-W-pump3  _(bn=4, lv=3)_

|  |  |
|---|---|
| term.154 MS-W-pump3 |  |
| rawValue 1 |  |
| termVal auto |  |


### diagrams  _(bn=5, lv=1)_

|  |  |
|---|---|
| diagrams |  |
| sysDiagram 57133 |  |
| typeSensor 0 |  |
| type-HP1 MXF12D9E8-1 |  |
| easySetup 1 |  |
| longDes heat pump 1 |  |
| maxSP 70.0 °C |  |
| boost.hCu 0.0 °C |  |
| BoosterH 0 |  |
| longDes buffer tank |  |
| boostZ1 2.0 |  |
| longDes domHotWater |  |
| SP-OT1 45.0 °C |  |
| SP-OT2 45.0 °C |  |
| SP-NO 2.0 °C |  |
| maxSP 70.0 °C |  |
| maxDemFl-T 70.0 °C |  |
| thermDes 0 |  |
| longDes heatC. 1 |  |
| room compens. 0 |  |
| hCu-slope 0.5 |  |
| hCu-exp 1.10 |  |
| roomOT1 22.0 °C |  |
| roomOT2 22.0 °C |  |
| roomNO 15.0 °C |  |
| maxFl 65.0 °C |  |
| longDes heatC. 2 |  |
| room compens. 0 |  |
| hCu-slope 0.5 |  |
| hCu-exp 1.10 |  |
| roomOT1 22.0 °C |  |
| roomOT2 22.0 °C |  |
| roomNO 15.0 °C |  |
| maxFl 65.0 °C |  |
| cold start 0 |  |


### system survey  _(bn=6, lv=1)_

|  |
|---|
| system survey |
| controller |
| heatC. 1 |
| heatC. 2 |
| domHotWater |
| buffer tank |
| heat pump 1 |
| inputs |
| outputs |


#### controller  _(bn=1, lv=2)_

|  |  |
|---|---|
| system controller |  |
| RU_type PAW-HPM1 |  |
| DIAGRAM 57133 LDT. |  |
| progDat 06.01.16 |  |
| version H1.1.26 |  |
| prodNo 011411060723 |  |
| curTime 21:06 |  |
| curDate 22.05.26 |  |


#### heatC. 1  _(bn=2, lv=2)_

|  |  |
|---|---|
| system heatCirc.1 |  |
| roomOT1 20.0 °C |  |
| roomOT2 20.0 °C |  |
| roomNO 20.0 °C |  |
| opStatus nom. oper. OT1 |  |
| trouble normal |  |
| source timer-OT1 ---------- |  |
| outdoor 18.0 °C |  |
| SP-Flow 20.0 °C |  |
| flow 21.3 °C |  |
| pump on |  |
| Y-contr. 0.0 % |  |


#### heatC. 2  _(bn=3, lv=2)_

|  |  |
|---|---|
| system heatCirc.2 |  |
| roomOT1 45.0 °C |  |
| roomOT2 19.0 °C |  |
| roomNO 22.0 °C |  |
| opStatus nom. oper. OT2 |  |
| trouble normal |  |
| source timer-OT2 ---------- |  |
| outdoor 18.0 °C |  |
| SP-Flow 18.0 °C |  |
| flow 17.1 °C |  |
| pump off |  |
| Y-contr. 0.0 % |  |


#### domHotWater  _(bn=4, lv=2)_

|  |  |
|---|---|
| system DHW.1 |  |
| SP-OT1 52.0 °C |  |
| SP-OT2 45.0 °C |  |
| SP-NO 2.0 °C |  |
| opStatus nom. oper. OT2 |  |
| trouble normal |  |
| source timer-OT2 ----- |  |
| SP-DHWta 45.0 °C |  |
| DHWtank 49.0 °C |  |


#### buffer tank  _(bn=5, lv=2)_

|  |  |
|---|---|
| system buffer |  |
| opStatus nom. oper. |  |
| trouble normal |  |
| SP-zone1 20.0 °C |  |
| buffer1 34.3 |  |


#### heat pump 1  _(bn=6, lv=2)_

|  |  |
|---|---|
| system heatPump1 |  |
| opStatus Blocked / off |  |
| trouble normal |  |
| source no demand |  |
| setpointHC 2 °C |  |
| setp.DHW 2 °C |  |
| HPOutletTemp 25 °C |  |
| HPInletTemp 24 °C |  |
| OP-OFF/ON off |  |
| OP-HEAT on |  |
| OP-TANK off |  |
| OP-FORCE off |  |
| Stat-Heater off |  |
| Stat-Booster off |  |
| Stat-Warning off |  |
| Stat-Defrost off |  |
| Errorcode --- |  |
| Freq 0 |  |
| ServiceOP off |  |
| StatEHeat 9 kW |  |
| Quiet off |  |


#### inputs  _(bn=7, lv=2)_

|  |  |
|---|---|
| system inputs |  |
| term.17 0.0 °C |  |
| term.18 21.3 °C |  |
| term.19 17.1 °C |  |
| term.20 0.0 °C |  |
| term.21 0.0 °C |  |
| term.22 34.3 °C |  |
| term.23 0.0 °C |  |
| term.24 0.0 °C |  |
| term.25 0 |  |
| term.26 0 |  |
| term.27 0.1 % |  |
| term.28 0.0 % |  |


#### outputs  _(bn=8, lv=2)_

|  |  |
|---|---|
| system outputs |  |
| term.01 0 |  |
| term.03 1 |  |
| term.05 0 |  |
| term.07 1 |  |
| term.09 0 |  |
| term.11 1 |  |
| term.13 0 |  |

