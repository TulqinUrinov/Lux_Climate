bool StartServer(void *self, int configStruct, int timeoutMs)
{
    // Step 1: Try to acquire write lock
    if (!WriteLock(self + 0x800f8))
    {
        log_error("StartServer: WriteLock Failed");
        return false;
    }

    // Step 2: Check required resources
    if (!CheckResources(self))
    {
        log_error("StartServer: CheckResource Failed");
        Unlock(self + 0x800f8);
        return false;
    }

    // Step 3: Make sure no links are already active
    if (getHRUDPLinkHandle(self) == -1 && getMQTTLinkHandle(self) == -1)
    {

        int linkType = *(int *)(self + 0x80154); // type: 0 = both, 1 = HRUDP, 2 = MQTT

        // ========== START HRUDP ========== //
        if (linkType == 0 || linkType == 1)
        {
            CreateLinkParams params{};
            params.type = 9;
            params.port = *(short *)(configStruct + 0x80);
            params.context = self;
            params.config = configStruct;
            params.handler = HRUDP_Handler;

            int handle = CoreBase_CreateServerLink(params);

            setHRUDPLinkHandle(self, handle);
            if (handle == -1)
            {
                log_error("StartServer: CoreBase_CreateServerLink HRUDP failed");
                Unlock(self + 0x800f8);
                return false;
            }

            log_info("StartServer: HRUDP Link created");
        }

        // ========== START MQTT ========== //
        if (linkType == 0 || linkType == 2)
        {
            CreateLinkParams params{};
            params.type = 0x18;
            params.port = *(short *)(configStruct + 0x80);
            params.context = self;
            params.config = configStruct;
            params.handler = MQTT_Handler;
            params.timeout = timeoutMs != 0 ? timeoutMs : 90000;

            int handle = CoreBase_CreateServerLink(params);

            setMQTTLinkHandle(self, handle);
            if (handle == -1)
            {
                log_error("StartServer: CoreBase_CreateServerLink MQTT failed");

                // Cleanup HRUDP if created
                if (getHRUDPLinkHandle(self) != -1)
                {
                    DestroyLink(getHRUDPLinkHandle(self));
                    setHRUDPLinkHandle(self, -1);
                }

                Unlock(self + 0x800f8);
                return false;
            }

            log_info("StartServer: MQTT Link created");
        }

        // ========== CREATE THREAD ========== //
        int threadHandle = CreateServerThread(self, 0x20000);
        setServerThreadHandle(self, threadHandle);

        if (threadHandle == 0)
        {
            log_sys_error("StartServer: HPR_Thread_Create Failed");
            Unlock(self + 0x800f8);
            return false;
        }

        Unlock(self + 0x800f8);
        return true;
    }
    else
    {
        log_error("StartServer: Links already exist");
        PrintCallstack();
        Unlock(self + 0x800f8);
        return false;
    }
}