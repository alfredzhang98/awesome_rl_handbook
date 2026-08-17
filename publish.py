# -*- coding: utf-8 -*-
"""重新切分讲义并发布到 GitHub。

用法：
    python publish.py                 # 有改动才提交并推送
    python publish.py -m "自定义信息"  # 指定 commit 信息
    python publish.py --quiet         # 无改动时不出声（给 hook 用）

失败（没网、没凭据等）时打印原因并以 0 退出，不打断调用方。
"""
import io
import os
import subprocess
import sys
import time

REPO = os.path.dirname(os.path.abspath(__file__))
SPLIT = os.path.join(REPO, "split_book.py")


def run(args, **kw):
    return subprocess.run(args, cwd=REPO, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", **kw)


def main():
    argv = sys.argv[1:]
    quiet = "--quiet" in argv
    msg = None
    if "-m" in argv:
        i = argv.index("-m")
        if i + 1 < len(argv):
            msg = argv[i + 1]

    def say(*a):
        print(*a)

    if not os.path.isdir(os.path.join(REPO, ".git")):
        say("publish: %s 不是 git 仓库，跳过" % REPO)
        return 0

    # 1) 重新切分
    r = run([sys.executable, SPLIT])
    if r.returncode != 0:
        say("publish: split_book.py 失败\n" + (r.stderr or r.stdout).strip()[-1500:])
        return 0

    # 2) 有改动才提交
    run(["git", "add", "-A"])
    if run(["git", "diff", "--cached", "--quiet"]).returncode == 0:
        if not quiet:
            say("publish: 没有改动，无需发布")
        return 0

    files = [l for l in run(["git", "diff", "--cached", "--name-only"]).stdout.splitlines() if l]
    if msg is None:
        msg = u"更新讲义并重新切分（%s）" % time.strftime("%Y-%m-%d %H:%M")
    body = msg + u"\n\nCo-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>\n"

    r = run(["git", "commit", "-F", "-"], input=body)
    if r.returncode != 0:
        say("publish: commit 失败\n" + (r.stderr or r.stdout).strip()[-1500:])
        return 0

    # 3) 推送
    r = run(["git", "push", "origin", "HEAD"])
    if r.returncode != 0:
        say("publish: 已在本地提交，但 push 失败（改动没丢，联网后 git push 即可）\n"
            + (r.stderr or r.stdout).strip()[-1500:])
        return 0

    sha = run(["git", "rev-parse", "--short", "HEAD"]).stdout.strip()
    say(u"publish: 已发布 %s · %d 个文件 · %s" % (sha, len(files), msg))
    say(u"          https://alfredzhang98.github.io/rl-handbook-cartpole/")
    return 0


if __name__ == "__main__":
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    sys.exit(main())
