
int NET_ECMS_StartListen(int param_1)

{
  undefined *puVar1;
  int iVar2;
  int *piVar3;
  void *pvVar4;
  undefined4 uVar5;
  int iVar6;
  undefined4 local_18 [2];
  int local_10;
  int local_c;
  int local_8;
  
                    /* 0x66d50  104  NET_ECMS_StartListen */
  puVar1 = FUN_100743f0();
  iVar2 = FUN_1008e940((int)puVar1);
  if (iVar2 == 0) {
    local_c = -1;
  }
  else {
    puVar1 = FUN_100743f0();
    iVar2 = FUN_1008f080((int)puVar1);
    FUN_100265e0(local_18,iVar2);
    if (param_1 == 0) {
      FUN_100754a0(1,(byte *)"NET_ECMS_StartListen, lpCMSListenPara == NULL");
      FUN_100751c0((LPVOID)0x11);
      local_c = -1;
      FUN_10026650(local_18);
    }
    else {
      local_8 = -1;
      piVar3 = (int *)FUN_1003d260();
      iVar2 = FUN_1003de10(piVar3);
      if (iVar2 == 0) {
        FUN_100751c0((LPVOID)0x11);
        FUN_100754a0(1,(byte *)"NET_ECMS_StartListen, LockInterface Failed");
      }
      else {
        uVar5 = *(undefined4 *)(param_1 + 0x88);
        iVar2 = *(int *)(param_1 + 0x84);
        pvVar4 = (void *)FUN_1003d260();
        iVar2 = FUN_100407b0(pvVar4,iVar2,uVar5);
        if (iVar2 == 0) {
          FUN_100750c0();
          FUN_100754a0(1,(byte *)"NET_ECMS_StartListen, StartWork Failed, error[%d]");
        }
        else {
          iVar2 = *(int *)(param_1 + 0x8c) * *(int *)(param_1 + 0x90) * 1000;
          pvVar4 = (void *)FUN_100456c0();
          iVar2 = FUN_1004c100(pvVar4,param_1,iVar2);
          if (iVar2 == 0) {
            FUN_100750c0();
            FUN_100754a0(1,(byte *)"NET_ECMS_StartListen, StartServer Failed, error[%d]");
            iVar6 = 1;
            iVar2 = 0;
            pvVar4 = (void *)FUN_1003d260();
            FUN_10040aa0(pvVar4,iVar2,iVar6);
          }
          else {
            local_8 = 0;
          }
        }
        piVar3 = (int *)FUN_1003d260();
        FUN_10040c90(piVar3);
      }
      if (local_8 != -1) {
        FUN_100751c0((LPVOID)0x0);
      }
      local_10 = local_8;
      FUN_10026650(local_18);
      local_c = local_10;
    }
  }
  return local_c;
}