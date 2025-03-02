"""View functions for PDM Lite."""
from flask import render_template, session, redirect, flash
import db

def user_page():
    """Displays the user page with advanced statistics."""
    if "username" in session:
        username = session["username"]
        user_items_rows = db.get_items_by_user(username)
        user_items = []
        for row in user_items_rows:
            user_items.append(dict(row))

        # Get advanced statistics
        total_items_related_to_user = len(user_items)
        item_type_counts = {}
        for item in user_items:
            item_type = item['item_type']
            item_type_counts[item_type] = item_type_counts.get(item_type, 0) + 1

        # Get most used components created by user
        user_most_used = db.query("""
            SELECT 
                i.item_number, 
                i.description,
                COUNT(DISTINCT a.assembly_item_number) as used_in_assemblies,
                SUM(a.quantity) as total_quantity
            FROM 
                items i
            JOIN 
                assemblies a ON i.item_number = a.component_item_number
            WHERE 
                i.creator = ?
            GROUP BY 
                i.item_number
            ORDER BY 
                used_in_assemblies DESC, total_quantity DESC
            LIMIT 5
        """, [username])

        # Get largest assemblies created by user
        user_largest_assemblies = db.query("""
            SELECT 
                i.item_number,
                i.description,
                COUNT(a.component_item_number) as component_count,
                SUM(a.quantity) as total_parts
            FROM 
                items i
            JOIN 
                assemblies a ON i.item_number = a.assembly_item_number
            WHERE 
                i.creator = ?
            GROUP BY 
                i.item_number
            ORDER BY 
                component_count DESC, total_parts DESC
            LIMIT 5
        """, [username])

        return render_template(
            "user_page.html",
            username=username,
            user_items=user_items,
            total_items_created=total_items_related_to_user,
            item_type_counts=item_type_counts,
            most_used_components=user_most_used,
            largest_assemblies=user_largest_assemblies
        )
    return redirect("/")

def item_details(item_number):
    """Display detailed information about an item and its revision history."""
    if "username" not in session:
        return redirect("/")

    item = db.get_item_by_number(item_number)
    if not item:
        flash("Item not found", "error")
        return redirect("/pdm")

    revisions = db.get_item_revisions(item_number)

    # Get specific details based on item type
    specific_details = None
    bom_items = []

    if item["item_type"] == "Manufactured Part":
        specific_details = db.get_manufactured_part_details(item_number)
    elif item["item_type"] == "Fixed Part":
        specific_details = db.get_fixed_part_details(item_number)
    elif item["item_type"] == "Assembly":
        # Get BOM items for this assembly
        bom_items = db.get_assembly_bom(item_number)

    return render_template(
        "item_details.html", 
        item=item,
        specific_details=specific_details,
        bom_items=bom_items,
        revisions=revisions,
        username=session["username"]
    )

def statistics():
    """Display overall PDM statistics"""
    if "username" not in session:
        return redirect("/")
    # Get overall item statistics
    item_stats = db.get_item_usage_statistics()

    # Get most used components
    most_used = db.get_most_used_components(10)

    # Get largest assemblies
    largest_assemblies = db.get_largest_assemblies(10)

    # Get unused items
    unused_items = db.get_items_without_usage()

    # Get user contribution stats
    user_stats = db.get_user_contribution_stats()

    return render_template(
        "statistics.html",
        username=session["username"],
        item_stats=item_stats,
        most_used=most_used,
        largest_assemblies=largest_assemblies,
        unused_items=unused_items,
        user_stats=user_stats
    )
