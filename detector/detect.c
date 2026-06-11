/*
 * detect.c — DocToMD hardware detector
 * No external dependencies. Outputs JSON to stdout.
 * Compile: cmake -B build && cmake --build build
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifdef _WIN32
  #include <windows.h>
#else
  #include <unistd.h>
#endif

/* ── helpers ─────────────────────────────────────────────────────────── */

static void trim_newline(char *s) {
    size_t len = strlen(s);
    while (len > 0 && (s[len-1] == '\n' || s[len-1] == '\r' || s[len-1] == ' '))
        s[--len] = '\0';
}

/* Run cmd, store first line of stdout in out (max out_sz bytes).
   Returns 1 on success, 0 if command not found or failed. */
static int run_cmd_first_line(const char *cmd, char *out, size_t out_sz) {
    FILE *fp;
#ifdef _WIN32
    fp = _popen(cmd, "r");
#else
    fp = popen(cmd, "r");
#endif
    if (!fp) return 0;
    int ok = (fgets(out, (int)out_sz, fp) != NULL);
#ifdef _WIN32
    _pclose(fp);
#else
    int status = pclose(fp);
    if (status != 0) ok = 0;
#endif
    if (ok) trim_newline(out);
    return ok;
}

/* ── GPU detection ───────────────────────────────────────────────────── */

/* nvidia-smi --query-gpu=driver_version,memory.total --format=csv,noheader,nounits
   Returns "driver_ver, vram_mb" e.g. "552.12, 8192" */
static int detect_nvidia(char *driver, size_t dsz, long *vram_mb) {
    char buf[256] = {0};
    /* query driver version */
    if (!run_cmd_first_line(
            "nvidia-smi --query-gpu=driver_version --format=csv,noheader,nounits 2>nul",
            buf, sizeof(buf)))
        return 0;
    strncpy(driver, buf, dsz - 1);

    /* query vram */
    char vbuf[64] = {0};
    if (run_cmd_first_line(
            "nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits 2>nul",
            vbuf, sizeof(vbuf))) {
        *vram_mb = atol(vbuf);
    } else {
        *vram_mb = 0;
    }
    return 1;
}

/* CUDA version from nvidia-smi top line: "CUDA Version: 12.4" */
static void detect_cuda_version(char *cuda_ver, size_t csz) {
    char buf[256] = {0};
    if (!run_cmd_first_line("nvidia-smi 2>nul", buf, sizeof(buf))) {
        strncpy(cuda_ver, "unknown", csz - 1);
        return;
    }
    /* Search for "CUDA Version: X.Y" */
    const char *p = strstr(buf, "CUDA Version:");
    if (!p) {
        /* Try second approach: nvidia-smi --query --display=COMPUTE */
        strncpy(cuda_ver, "unknown", csz - 1);
        return;
    }
    p += strlen("CUDA Version:");
    while (*p == ' ') p++;
    size_t i = 0;
    while (*p && *p != ' ' && *p != '\n' && *p != '|' && i < csz - 1)
        cuda_ver[i++] = *p++;
    cuda_ver[i] = '\0';
}

/* rocm-smi exists → AMD GPU */
static int detect_amd(long *vram_mb) {
    char buf[256] = {0};
    /* rocm-smi --showmeminfo vram --csv */
    if (!run_cmd_first_line("rocm-smi --showproductname 2>nul", buf, sizeof(buf)))
        return 0;
    *vram_mb = 0; /* rocm-smi VRAM parsing varies; leave 0 as safe default */
    return 1;
}

/* ── RAM detection ───────────────────────────────────────────────────── */

static long detect_ram_mb(void) {
#ifdef _WIN32
    MEMORYSTATUSEX ms;
    ms.dwLength = sizeof(ms);
    if (GlobalMemoryStatusEx(&ms))
        return (long)(ms.ullTotalPhys / (1024 * 1024));
    return 0;
#else
    FILE *f = fopen("/proc/meminfo", "r");
    if (!f) return 0;
    char line[128];
    long kb = 0;
    while (fgets(line, sizeof(line), f)) {
        if (strncmp(line, "MemTotal:", 9) == 0) {
            sscanf(line + 9, "%ld", &kb);
            break;
        }
    }
    fclose(f);
    return kb / 1024;
#endif
}

/* ── CPU vendor ──────────────────────────────────────────────────────── */

static void detect_cpu_vendor(char *vendor, size_t vsz) {
#ifdef _WIN32
    /* Use CPUID instruction via __cpuid intrinsic */
    int regs[4] = {0};
    __cpuid(regs, 0);
    char v[13] = {0};
    memcpy(v,     &regs[1], 4);
    memcpy(v + 4, &regs[3], 4);
    memcpy(v + 8, &regs[2], 4);
    v[12] = '\0';
    if (strstr(v, "Intel"))      strncpy(vendor, "Intel", vsz - 1);
    else if (strstr(v, "AMD") || strstr(v, "Auth"))  strncpy(vendor, "AMD", vsz - 1);
    else                         strncpy(vendor, v, vsz - 1);
#else
    FILE *f = fopen("/proc/cpuinfo", "r");
    if (!f) { strncpy(vendor, "unknown", vsz - 1); return; }
    char line[256];
    while (fgets(line, sizeof(line), f)) {
        if (strncmp(line, "vendor_id", 9) == 0) {
            char *p = strchr(line, ':');
            if (p) {
                p++; while (*p == ' ') p++;
                trim_newline(p);
                if (strstr(p, "Intel"))     strncpy(vendor, "Intel", vsz - 1);
                else if (strstr(p, "AMD"))  strncpy(vendor, "AMD", vsz - 1);
                else                        strncpy(vendor, p, vsz - 1);
                fclose(f);
                return;
            }
        }
    }
    fclose(f);
    strncpy(vendor, "unknown", vsz - 1);
#endif
}

/* ── main ────────────────────────────────────────────────────────────── */

int main(void) {
    char gpu[16]          = "none";
    char cuda_ver[32]     = "n/a";
    char driver[64]       = "n/a";
    long vram_mb          = 0;
    long ram_mb           = detect_ram_mb();
    char cpu_vendor[32]   = "unknown";

    detect_cpu_vendor(cpu_vendor, sizeof(cpu_vendor));

    if (detect_nvidia(driver, sizeof(driver), &vram_mb)) {
        strncpy(gpu, "nvidia", sizeof(gpu) - 1);
        /* nvidia-smi first line contains CUDA Version; need full first line */
        char smi_line[512] = {0};
        /* Read full first line of nvidia-smi to extract CUDA version */
        FILE *fp;
#ifdef _WIN32
        fp = _popen("nvidia-smi 2>nul", "r");
#else
        fp = popen("nvidia-smi 2>/dev/null", "r");
#endif
        if (fp) {
            /* Skip header lines to find "CUDA Version:" */
            char line[512];
            int found = 0;
            while (fgets(line, sizeof(line), fp) && !found) {
                const char *p = strstr(line, "CUDA Version:");
                if (p) {
                    p += strlen("CUDA Version:");
                    while (*p == ' ') p++;
                    size_t i = 0;
                    while (*p && *p != ' ' && *p != '\n' && *p != '|' && i < sizeof(cuda_ver) - 1)
                        cuda_ver[i++] = *p++;
                    cuda_ver[i] = '\0';
                    found = 1;
                }
            }
#ifdef _WIN32
            _pclose(fp);
#else
            pclose(fp);
#endif
        }
    } else if (detect_amd(&vram_mb)) {
        strncpy(gpu, "amd", sizeof(gpu) - 1);
    }

    /* Escape strings for JSON safety (basic: no quotes in hw strings) */
    printf("{\n");
    printf("  \"gpu\": \"%s\",\n",         gpu);
    printf("  \"cuda_version\": \"%s\",\n", cuda_ver);
    printf("  \"driver_version\": \"%s\",\n", driver);
    printf("  \"vram_mb\": %ld,\n",        vram_mb);
    printf("  \"ram_mb\": %ld,\n",         ram_mb);
    printf("  \"cpu_vendor\": \"%s\"\n",   cpu_vendor);
    printf("}\n");

    return 0;
}
