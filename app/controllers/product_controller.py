from app.models import db, Product, Supplier

class ProductController:

    @staticmethod
    def get_all_products():
        products = Product.query.all()
        return {'success': True, 'products': [p.to_dict() for p in products]}

    @staticmethod
    def get_product_by_id(product_id):
        product = Product.query.get(product_id)
        if not product:
            return {'success': False, 'message': 'Producto no encontrado'}
        return {'success': True, 'product': product.to_dict()}

    @staticmethod
    def create_product(name, description, price, stock, supplier_id=None):
        if Product.query.filter_by(name=name).first():
            return {'success': False, 'message': 'Ya existe un producto con ese nombre'}

        # Opcional: Verificar si el supplier_id existe
        if supplier_id:
            supplier = Supplier.query.get(supplier_id)
            if not supplier:
                return {'success': False, 'message': 'Proveedor no encontrado'}

        new_product = Product(
            name=name,
            description=description,
            price=price,
            stock=stock,
            supplier_id=supplier_id
        )
        db.session.add(new_product)
        db.session.commit()
        return {'success': True, 'message': 'Producto creado exitosamente', 'product': new_product.to_dict()}

    @staticmethod
    def update_product(product_id, name=None, description=None, price=None, stock=None, supplier_id=None):
        product = Product.query.get(product_id)
        if not product:
            return {'success': False, 'message': 'Producto no encontrado'}

        if name:
            product.name = name
        if description is not None: # Permitir que la descripción sea None/vacía
            product.description = description
        if price is not None:
            product.price = price
        if stock is not None:
            product.stock = stock
        if supplier_id is not None: # Permitir cambiar el proveedor o quitarlo
            if supplier_id == '': # Si se envía vacío para quitar el proveedor
                product.supplier_id = None
            else:
                supplier = Supplier.query.get(supplier_id)
                if not supplier:
                    return {'success': False, 'message': 'Proveedor no encontrado'}
                product.supplier_id = supplier_id

        db.session.commit()
        return {'success': True, 'message': 'Producto actualizado exitosamente', 'product': product.to_dict()}

    @staticmethod
    def delete_product(product_id):
        product = Product.query.get(product_id)
        if not product:
            return {'success': False, 'message': 'Producto no encontrado'}
        db.session.delete(product)
        db.session.commit()
        return {'success': True, 'message': 'Producto eliminado exitosamente'}