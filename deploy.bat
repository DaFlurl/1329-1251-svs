@echo off
echo 🚀 Deploying AgentDaf1 Scoreboard to GitHub Pages...
echo.

REM Switch to gh-pages branch
git checkout gh-pages

REM Merge latest changes from main
git merge main --no-edit

REM Push to GitHub Pages
git push origin gh-pages

REM Switch back to main
git checkout main

echo.
echo ✅ Deployment complete!
echo 📱 Scoreboard available at: https://daflurl.github.io/1329-1251-svs/scoreboard.html
echo.
pause