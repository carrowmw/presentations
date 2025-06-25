Deploying a Subfolder to a New Repository and GitHub Pages
This guide outlines how to take a subfolder from your main project (e.g., builds/cupum_build) and deploy it as a standalone GitHub Pages website in a separate repository.

Step 1: Split the Build Folder into a New Branch
First, you need to create a new branch in your local repository that contains only the contents and history of your builds/cupum_build folder. The git subtree command is perfect for this.

Run the following command in your terminal from the root of your main project repository:

git subtree split --prefix=builds/cupum_build -b gh-pages

What this command does:

git subtree split: This is the command for splitting a subdirectory into a new branch.

--prefix=builds/cupum_build: This tells Git which folder you want to split off.

-b gh-pages: This creates a new branch named gh-pages to store the result. Using gh-pages is a standard convention for branches that will be deployed to GitHub Pages.

After running this, you will have a new local branch named gh-pages that contains only the contents of your build folder.

Step 2: Push the New Branch to Your New Remote Repository
Next, you need to push the gh-pages branch to your new remote repository (which you've named cupum).

Run the following command:

git push cupum gh-pages

What this command does:

git push cupum: This specifies that you are pushing to your new remote repository.

gh-pages: This tells Git to push the gh-pages branch. A branch of the same name will be created on the remote repository.

Step 3: Configure GitHub Pages
Finally, you need to tell GitHub to serve your site from the new branch you just pushed.

Navigate to your new GitHub repository on the web (the one associated with the cupum remote).

Click on the Settings tab.

In the left sidebar, click on Pages.

Under the "Build and deployment" section, for the Source, select Deploy from a branch.

Under "Branch", select the gh-pages branch from the dropdown menu and leave the folder as /(root).

Click Save.

GitHub will now build your site from the gh-pages branch. After a minute or two, your presentation will be live at the URL shown on the Pages settings screen (usually https://<your-username>.github.io/<your-repo-name>/).

Step 4: Updating the Deployed Site
Once you make changes to your project and update the builds/cupum_build directory, you'll need to update the gh-pages branch and push it again.

Commit Your Changes: First, make sure you've committed all the latest changes to your main branch.

git add .
git commit -m "Update build folder with new changes"

Re-run the Subtree Split: Run the exact same subtree command as before. This will regenerate the gh-pages branch with the latest contents of your build directory, overwriting the old version of the branch.

git subtree split --prefix=builds/cupum_build -b gh-pages

Force Push the Branch: Because the history of the gh-pages branch is rewritten every time you run the split command, you need to "force push" it to your cupum remote. This tells Git to replace the remote branch with your new local one.

git push cupum gh-pages --force

Note: The --force flag is necessary and safe in this specific case because the gh-pages branch is being used purely for deployment.

Your GitHub Pages site will automatically redeploy with the latest changes. This usually takes a minute or two.
