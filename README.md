# ObsidianVaultToTempora
Script to automate the process of converting an obsidian file system into Tempora compatible markdowns.

Below you will find the functionality that the script provides:

**1)**

 It will search through all folders in a specified directory (ie a copied obsidian vault) and it will rename any folders called “attachments” to “assets”.

**2)**

It will standardise the image references (as obsidian allows for image scaling, and obsidian doesn't use src references so the obsidian image references don't work in Typora)

​	<u>For example:</u>

​	![[Pasted image 20250412122934.png|500]]

​	Goes to 

​	![Pasted image 20250412122934](./assets/Pasted image 20250412122934.PNG)

This was a big time saver and essential for enabling a smooth transition from obsidian.

**3)**

It will remove any incompatible callouts for block quotes (e.g. [!definition] in obsidian) and if there is text next to the callout which works in obsidian but not typora it will move the text to the next line and put it in bold.

> <u>Example 1:</u>
>
> \>[!defintion] This is a definition
>
> Goes to:
>
> \> **This is a definition**

> <u>Example 2:</u>
>
> \>[!note] Definition of programming:
>
> \>This is the definition of programming
>
> Goes to:
>
> \>[!note]
>
> \>**Definition of programming:**
>
> \>This is the definition of programming